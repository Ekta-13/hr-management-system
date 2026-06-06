"""
utils/file_handler.py — Secure file upload and save logic
"""
import os
import uuid
from pathlib import Path
from config import RESUME_DIR, MEDIA_DIR, ONBOARDING_DIR


def save_resume(file_bytes: bytes, original_name: str, candidate_id: int) -> str:
    ext = Path(original_name).suffix.lower()
    filename = f"candidate_{candidate_id}_{uuid.uuid4().hex[:8]}{ext}"
    path = RESUME_DIR / filename
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)


def save_interview_media(file_bytes: bytes, original_name: str, application_id: int) -> str:
    ext = Path(original_name).suffix.lower()
    filename = f"interview_{application_id}_{uuid.uuid4().hex[:8]}{ext}"
    path = MEDIA_DIR / filename
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)


def save_onboarding_doc(file_bytes: bytes, original_name: str, candidate_id: int) -> str:
    ext = Path(original_name).suffix.lower()
    safe_name = original_name.replace(" ", "_")
    filename = f"onboard_{candidate_id}_{uuid.uuid4().hex[:8]}_{safe_name}"
    path = ONBOARDING_DIR / filename
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)
