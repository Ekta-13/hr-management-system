"""
database/db.py — SQLite connection, initialisation, and query helpers
"""
import sqlite3
import bcrypt
import json
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "hr.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables and seed default admin user."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    _seed_admin(conn)
    conn.close()


def _seed_admin(conn):
    existing = conn.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
    if existing:
        return
    pw_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    conn.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?,?,?,?)",
        ("admin", "admin@hrms.com", pw_hash, "admin"),
    )
    conn.commit()


# ── Generic helpers ──────────────────────────────────────────

def fetchone(query: str, params: tuple = ()):
    conn = get_connection()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None


def fetchall(query: str, params: tuple = ()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def execute(query: str, params: tuple = ()):
    conn = get_connection()
    cur = conn.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# ── User helpers ─────────────────────────────────────────────

def create_user(username, email, password, role):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?,?,?,?)",
        (username, email, pw_hash, role),
    )


def verify_user(username, password):
    row = fetchone("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return row
    return None


def get_user_by_id(user_id):
    return fetchone("SELECT * FROM users WHERE id=?", (user_id,))


def get_all_users():
    return fetchall("SELECT id, username, email, role, is_active, created_at FROM users ORDER BY created_at DESC")


def toggle_user_active(user_id, is_active):
    execute("UPDATE users SET is_active=? WHERE id=?", (is_active, user_id))


# ── Candidate helpers ─────────────────────────────────────────

def create_candidate_profile(user_id, full_name, phone="", location=""):
    return execute(
        "INSERT INTO candidates (user_id, full_name, phone, location) VALUES (?,?,?,?)",
        (user_id, full_name, phone, location),
    )


def get_candidate_by_user(user_id):
    return fetchone("SELECT * FROM candidates WHERE user_id=?", (user_id,))


def get_candidate_by_id(candidate_id):
    return fetchone("SELECT * FROM candidates WHERE id=?", (candidate_id,))


def update_candidate(candidate_id, **kwargs):
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [candidate_id]
    execute(f"UPDATE candidates SET {fields} WHERE id=?", tuple(values))


def get_all_candidates():
    return fetchall("""
        SELECT c.*, u.email, u.username, u.is_active
        FROM candidates c JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    """)


# ── Recruiter helpers ─────────────────────────────────────────

def create_recruiter_profile(user_id, full_name, department="", phone=""):
    return execute(
        "INSERT INTO recruiters (user_id, full_name, department, phone) VALUES (?,?,?,?)",
        (user_id, full_name, department, phone),
    )


def get_recruiter_by_user(user_id):
    return fetchone("SELECT * FROM recruiters WHERE user_id=?", (user_id,))


def get_all_recruiters():
    return fetchall("""
        SELECT r.*, u.email, u.username
        FROM recruiters r JOIN users u ON r.user_id = u.id
        ORDER BY r.created_at DESC
    """)


# ── Job helpers ───────────────────────────────────────────────

def create_job(recruiter_id, title, description, required_skills, location="", job_type="full-time", experience_required=0, salary_range=""):
    return execute(
        """INSERT INTO jobs (recruiter_id, title, description, required_skills, location, job_type, experience_required, salary_range)
           VALUES (?,?,?,?,?,?,?,?)""",
        (recruiter_id, title, description, required_skills, location, job_type, experience_required, salary_range),
    )


def get_all_jobs(status=None):
    if status:
        return fetchall("SELECT * FROM jobs WHERE status=? ORDER BY created_at DESC", (status,))
    return fetchall("SELECT * FROM jobs ORDER BY created_at DESC")


def get_job_by_id(job_id):
    return fetchone("SELECT * FROM jobs WHERE id=?", (job_id,))


def update_job(job_id, **kwargs):
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [job_id]
    execute(f"UPDATE jobs SET {fields} WHERE id=?", tuple(values))


def delete_job(job_id):
    execute("DELETE FROM jobs WHERE id=?", (job_id,))


def get_jobs_by_recruiter(recruiter_id):
    return fetchall("SELECT * FROM jobs WHERE recruiter_id=? ORDER BY created_at DESC", (recruiter_id,))


# ── Application helpers ───────────────────────────────────────

def create_application(candidate_id, job_id, cover_letter=""):
    return execute(
        "INSERT INTO applications (candidate_id, job_id, cover_letter) VALUES (?,?,?)",
        (candidate_id, job_id, cover_letter),
    )


def get_applications_for_job(job_id):
    return fetchall("""
        SELECT a.*, c.full_name, c.skills, c.experience_years, c.resume_path, u.email
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE a.job_id=?
        ORDER BY a.applied_at DESC
    """, (job_id,))


def get_applications_for_candidate(candidate_id):
    return fetchall("""
        SELECT a.*, j.title as job_title, j.location, j.status as job_status
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.candidate_id=?
        ORDER BY a.applied_at DESC
    """, (candidate_id,))


def update_application_status(app_id, status):
    execute("UPDATE applications SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, app_id))


def get_application_by_id(app_id):
    return fetchone("SELECT * FROM applications WHERE id=?", (app_id,))


def get_all_applications():
    return fetchall("""
        SELECT a.*, c.full_name, j.title as job_title
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        ORDER BY a.applied_at DESC
    """)


# ── Resume Score helpers ──────────────────────────────────────

def save_resume_score(application_id, match_score, matching_skills, missing_skills, ai_summary=""):
    existing = fetchone("SELECT id FROM resume_scores WHERE application_id=?", (application_id,))
    if existing:
        execute(
            """UPDATE resume_scores SET match_score=?, matching_skills=?, missing_skills=?, ai_summary=?, scored_at=CURRENT_TIMESTAMP
               WHERE application_id=?""",
            (match_score, matching_skills, missing_skills, ai_summary, application_id),
        )
    else:
        execute(
            """INSERT INTO resume_scores (application_id, match_score, matching_skills, missing_skills, ai_summary)
               VALUES (?,?,?,?,?)""",
            (application_id, match_score, matching_skills, missing_skills, ai_summary),
        )


def get_resume_score(application_id):
    return fetchone("SELECT * FROM resume_scores WHERE application_id=?", (application_id,))


def get_top_candidates_for_job(job_id, limit=10):
    return fetchall("""
        SELECT a.id as app_id, a.candidate_id, c.full_name, c.skills, c.experience_years,
               rs.match_score, rs.matching_skills, rs.missing_skills, a.status
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        LEFT JOIN resume_scores rs ON rs.application_id = a.id
        WHERE a.job_id=?
        ORDER BY rs.match_score DESC NULLS LAST
        LIMIT ?
    """, (job_id, limit))


# ── Interview helpers ─────────────────────────────────────────

def create_interview(application_id):
    existing = fetchone("SELECT id FROM interviews WHERE application_id=?", (application_id,))
    if existing:
        return existing["id"]
    return execute(
        "INSERT INTO interviews (application_id) VALUES (?)",
        (application_id,),
    )


def update_interview(interview_id, **kwargs):
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [interview_id]
    execute(f"UPDATE interviews SET {fields} WHERE id=?", tuple(values))


def get_interview_by_application(application_id):
    return fetchone("SELECT * FROM interviews WHERE application_id=?", (application_id,))


def save_interview_report(interview_id, comm, tech, conf, strengths, weaknesses, recommendation, feedback):
    overall = round((comm + tech + conf) / 3, 1)
    existing = fetchone("SELECT id FROM interview_reports WHERE interview_id=?", (interview_id,))
    if existing:
        execute(
            """UPDATE interview_reports SET communication_score=?, technical_score=?, confidence_score=?,
               overall_score=?, strengths=?, weaknesses=?, recommendation=?, detailed_feedback=?
               WHERE interview_id=?""",
            (comm, tech, conf, overall, strengths, weaknesses, recommendation, feedback, interview_id),
        )
    else:
        execute(
            """INSERT INTO interview_reports (interview_id, communication_score, technical_score, confidence_score,
               overall_score, strengths, weaknesses, recommendation, detailed_feedback)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (interview_id, comm, tech, conf, overall, strengths, weaknesses, recommendation, feedback),
        )


def get_interview_report(interview_id):
    return fetchone("SELECT * FROM interview_reports WHERE interview_id=?", (interview_id,))


# ── Onboarding helpers ────────────────────────────────────────

def create_onboarding(candidate_id):
    existing = fetchone("SELECT id FROM onboarding WHERE candidate_id=?", (candidate_id,))
    if existing:
        return existing["id"]
    default_checklist = json.dumps({
        "ID Proof": False, "Address Proof": False, "Educational Certificates": False,
        "Previous Experience Letter": False, "Bank Details": False, "PAN Card": False,
        "Passport Photo": False, "Signed Offer Letter": False,
    })
    return execute(
        "INSERT INTO onboarding (candidate_id, doc_checklist) VALUES (?,?)",
        (candidate_id, default_checklist),
    )


def get_onboarding(candidate_id):
    return fetchone("SELECT * FROM onboarding WHERE candidate_id=?", (candidate_id,))


def update_onboarding(candidate_id, **kwargs):
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [candidate_id]
    execute(f"UPDATE onboarding SET {fields}, updated_at=CURRENT_TIMESTAMP WHERE candidate_id=?", tuple(values))


# ── Analytics helpers ─────────────────────────────────────────

def get_platform_stats():
    return {
        "total_users": fetchone("SELECT COUNT(*) as c FROM users")["c"],
        "total_candidates": fetchone("SELECT COUNT(*) as c FROM candidates")["c"],
        "total_recruiters": fetchone("SELECT COUNT(*) as c FROM recruiters")["c"],
        "total_jobs": fetchone("SELECT COUNT(*) as c FROM jobs")["c"],
        "open_jobs": fetchone("SELECT COUNT(*) as c FROM jobs WHERE status='open'")["c"],
        "total_applications": fetchone("SELECT COUNT(*) as c FROM applications")["c"],
        "shortlisted": fetchone("SELECT COUNT(*) as c FROM applications WHERE status='shortlisted'")["c"],
        "hired": fetchone("SELECT COUNT(*) as c FROM applications WHERE status='hired'")["c"],
        "rejected": fetchone("SELECT COUNT(*) as c FROM applications WHERE status='rejected'")["c"],
        "interviews_completed": fetchone("SELECT COUNT(*) as c FROM interviews WHERE status='completed'")["c"],
    }
