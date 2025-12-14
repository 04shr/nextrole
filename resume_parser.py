import re
import PyPDF2
import docx

def extract_text(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text()

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = " ".join([p.text for p in doc.paragraphs])

    # 🔥 NORMALIZATION (VERY IMPORTANT)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)  # remove symbols
    text = re.sub(r"\s+", " ", text)          # normalize spaces

    return text
