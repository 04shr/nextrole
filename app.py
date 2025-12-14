import os
import requests
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from firebase_config import db
from resume_parser import extract_text
from match_engine import extract_skills, calculate_match

# ---------------------------
# App Config
# ---------------------------
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

# ---------------------------
# Helpers
# ---------------------------
def classify_experience(title):
    t = title.lower()
    if any(x in t for x in ["senior", "lead", "principal"]):
        return "Senior"
    if any(x in t for x in ["junior", "intern", "entry"]):
        return "Entry"
    return "Mid"

def classify_industry(title):
    t = title.lower()
    if "data" in t: return "Data & Analytics"
    if "software" in t: return "Software Engineering"
    if "finance" in t: return "Finance & FinTech"
    if "marketing" in t: return "Marketing"
    if "cloud" in t or "devops" in t: return "Cloud & DevOps"
    return "Other"

# ---------------------------
# API: JOBS (NO FILTERING HERE)
# ---------------------------
@app.route("/jobs", methods=["GET"])
def fetch_jobs():
    job_docs = db.collection("jobs").stream()
    jobs = [doc.to_dict() for doc in job_docs]
    return jsonify(jobs)

# ---------------------------
# API: DASHBOARD
# ---------------------------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    job_docs = db.collection("jobs").stream()

    total_jobs = 0
    role_count = {}
    experience_count = {}
    skill_count = {}
    location_count = {}

    for doc in job_docs:
        job = doc.to_dict()
        total_jobs += 1

        role = job.get("role", "Other")
        exp = job.get("experience_level", "Mid")
        location = job.get("location", "Unknown")

        role_count[role] = role_count.get(role, 0) + 1
        experience_count[exp] = experience_count.get(exp, 0) + 1
        location_count[location] = location_count.get(location, 0) + 1

        for skill in job.get("skills_required", []):
            skill = skill.lower()
            skill_count[skill] = skill_count.get(skill, 0) + 1

    top_role = max(role_count, key=role_count.get, default="N/A")
    top_skill = max(skill_count, key=skill_count.get, default="N/A")

    jobs_list = [doc.to_dict() for doc in db.collection("jobs").stream()]

    return jsonify({
    "total_jobs": total_jobs,
    "top_role": top_role,
    "top_skill": top_skill,
    "roles_distribution": role_count,
    "experience_distribution": experience_count,
    "jobs": jobs_list   # 🔥 ADD THIS
})


# ---------------------------
# API: RESUME MATCH
# ---------------------------
@app.route("/match-resume", methods=["POST"])
def match_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Invalid file type"}), 400

    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)

    resume_text = extract_text(path)
    resume_skills = extract_skills(resume_text)

    results = []
    job_docs = db.collection("jobs").stream()

    for doc in job_docs:
        job = doc.to_dict()
        job_skills = [s.lower() for s in job.get("skills_required", [])]
        if not job_skills:
            continue

        score, matched, missing = calculate_match(resume_skills, job_skills)

        if job.get("experience_level") == "Senior":
            score = max(score - 10, 0)

        results.append({
            "job_title": job.get("job_title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "job_url": job.get("job_url"),
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return jsonify({
        "resume_skills": resume_skills,
        "top_matches": results[:5]
    })

# ---------------------------
# HEALTH
# ---------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Job Analytics API running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
