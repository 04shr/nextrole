# ---------------------------
# Skill Vocabulary (Multi-Role)
# ---------------------------

COMMON_SKILLS = {
    # Data & Analytics
    "python", "sql", "excel", "power bi", "tableau",
    "statistics", "machine learning", "data analysis",
    "pandas", "numpy", "dashboard", "dashboards",

    # Software / Engineering
    "java", "javascript", "git", "rest api",
    "flask", "django", "react", "node",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes",
    "devops", "ci cd",

    # Marketing
    "seo", "google analytics", "campaign analysis",
    "marketing analytics",

    # Finance
    "financial analysis", "risk analysis",

    # Product / Management
    "stakeholder management", "roadmapping",
    "mentoring", "agile", "scrum"
}


# ---------------------------
# Normalize helper
# ---------------------------
def normalize(text):
    return text.lower().strip()


# ---------------------------
# Resume Skill Extraction
# ---------------------------
def extract_skills(resume_text):
    resume_text = normalize(resume_text)
    found = []

    for skill in COMMON_SKILLS:
        tokens = skill.split()
        if all(token in resume_text for token in tokens):
            found.append(skill)

    return list(set(found))


# ---------------------------
# Skill Weights (Role-Neutral)
# ---------------------------
SKILL_WEIGHTS = {
    # High impact
    "python": 3,
    "sql": 3,
    "machine learning": 3,
    "statistics": 3,

    # Medium impact
    "power bi": 2,
    "tableau": 2,
    "financial analysis": 2,
    "marketing analytics": 2,
    "risk analysis": 2,
    "aws": 2,
    "azure": 2,

    # Foundational
    "excel": 1,
    "numpy": 1,
    "pandas": 1,
    "git": 1,
    "react": 1,
    "docker": 1,
    "stakeholder management": 1,
    "mentoring": 1
}


# ---------------------------
# Match Scoring Logic
# ---------------------------
def calculate_match(resume_skills, job_skills):
    resume_set = set(resume_skills)
    job_set = set(job_skills)

    total_weight = 0
    matched_weight = 0

    matched = []
    missing = []

    for skill in job_set:
        weight = SKILL_WEIGHTS.get(skill, 1)
        total_weight += weight

        if skill in resume_set:
            matched_weight += weight
            matched.append(skill)
        else:
            missing.append(skill)

    score = int((matched_weight / total_weight) * 100) if total_weight else 0
    return score, matched, missing
