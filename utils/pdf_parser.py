"""
utils/pdf_parser.py — Extract structured info from resume PDFs using PyPDF2 + spaCy
"""
import re
import PyPDF2
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes."""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return ""


# ── Skill Keywords ─────────────────────────────────────────────
SKILL_KEYWORDS = [
    # Programming
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin",
    "scala", "r", "matlab", "perl", "bash", "shell",
    # Web
    "react", "angular", "vue", "node.js", "nodejs", "django", "flask", "fastapi", "spring", "express",
    "html", "css", "bootstrap", "tailwind", "next.js", "nextjs", "graphql", "rest", "restful",
    # Data / ML
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "keras",
    "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi",
    "data analysis", "data science", "statistics", "sql", "nosql",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins", "git", "github", "gitlab",
    "terraform", "ansible", "linux", "microservices", "devops",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "sqlite", "oracle", "cassandra",
    # Soft skills
    "leadership", "communication", "teamwork", "problem solving", "agile", "scrum", "jira",
]


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found.append(skill)
    return list(set(found))


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{3,5}[-\s\.]?[0-9]{4,6}", text)
    return match.group(0) if match else ""


def extract_name(text: str) -> str:
    """Heuristic: first non-empty line is usually the candidate's name."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return lines[0] if lines else "Unknown"


def extract_education(text: str) -> str:
    edu_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "m.e", "b.sc",
                    "m.sc", "mba", "bca", "mca", "degree", "university", "college", "institute"]
    lines = text.split("\n")
    edu_lines = []
    for line in lines:
        if any(k in line.lower() for k in edu_keywords):
            edu_lines.append(line.strip())
    return " | ".join(edu_lines[:3]) if edu_lines else "Not specified"


def extract_experience_years(text: str) -> int:
    patterns = [
        r"(\d+)\+?\s*years?\s*of\s*experience",
        r"(\d+)\+?\s*years?\s*experience",
        r"experience\s*of\s*(\d+)\+?\s*years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    return 0


def parse_resume(file_bytes: bytes) -> dict:
    """Return structured resume data from raw PDF bytes."""
    text = extract_text_from_pdf(file_bytes)
    if not text:
        return {"error": "Could not extract text from PDF", "raw_text": ""}
    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text),
    }
