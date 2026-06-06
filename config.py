"""
config.py — Centralised configuration for the HR Management System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESUME_DIR = UPLOAD_DIR / "resumes"
MEDIA_DIR = UPLOAD_DIR / "interview_media"
ONBOARDING_DIR = UPLOAD_DIR / "onboarding_docs"

for d in [RESUME_DIR, MEDIA_DIR, ONBOARDING_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ── App Settings ───────────────────────────────────────────────
APP_TITLE = "AI-Powered HR Management System"
APP_ICON = "🧠"
SESSION_TIMEOUT_MINUTES = 60

# ── AI Model Settings ──────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENAI_MODEL = "gpt-4o-mini"
WHISPER_MODEL = "base"   # base is fast; use "small" or "medium" for better accuracy

# ── Resume Scoring Thresholds ──────────────────────────────────
SCORE_EXCELLENT = 75
SCORE_GOOD = 50
SCORE_AVERAGE = 30

# ── Roles ──────────────────────────────────────────────────────
ROLE_ADMIN = "admin"
ROLE_RECRUITER = "recruiter"
ROLE_CANDIDATE = "candidate"
