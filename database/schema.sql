-- ============================================================
-- AI-Powered HR Management System — Database Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'recruiter', 'candidate')),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    location TEXT,
    skills TEXT,
    education TEXT,
    experience_years INTEGER DEFAULT 0,
    resume_path TEXT,
    linkedin_url TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'hired', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recruiters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    department TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recruiter_id INTEGER,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT,
    location TEXT,
    job_type TEXT DEFAULT 'full-time',
    experience_required INTEGER DEFAULT 0,
    salary_range TEXT,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed', 'draft')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recruiter_id) REFERENCES recruiters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'screening', 'shortlisted', 'interview', 'offered', 'rejected', 'hired')),
    cover_letter TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE(candidate_id, job_id)
);

CREATE TABLE IF NOT EXISTS resume_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER UNIQUE NOT NULL,
    match_score REAL DEFAULT 0.0,
    matching_skills TEXT,
    missing_skills TEXT,
    experience_match INTEGER DEFAULT 0,
    education_match INTEGER DEFAULT 0,
    ai_summary TEXT,
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER UNIQUE NOT NULL,
    media_path TEXT,
    transcript TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'uploaded', 'processing', 'completed', 'failed')),
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interview_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interview_id INTEGER UNIQUE NOT NULL,
    communication_score REAL DEFAULT 0.0,
    technical_score REAL DEFAULT 0.0,
    confidence_score REAL DEFAULT 0.0,
    overall_score REAL DEFAULT 0.0,
    strengths TEXT,
    weaknesses TEXT,
    recommendation TEXT CHECK(recommendation IN ('strong_hire', 'hire', 'consider', 'reject')),
    detailed_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS onboarding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER UNIQUE NOT NULL,
    offer_status TEXT DEFAULT 'pending' CHECK(offer_status IN ('pending', 'sent', 'accepted', 'declined')),
    offer_letter_path TEXT,
    joining_date DATE,
    joining_status TEXT DEFAULT 'pending' CHECK(joining_status IN ('pending', 'confirmed', 'joined', 'no_show')),
    doc_checklist TEXT DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);
