# 🧠 AI-Powered HR Management System

An intelligent HR automation platform that streamlines recruitment and onboarding using Artificial Intelligence. Built with Python, Streamlit, SQLite, Sentence Transformers, and OpenAI.

---

## 🎯 Problem Statement

Traditional hiring is slow, biased, and manual. Recruiters spend hours reading resumes, scheduling interviews, and tracking candidates. This system automates the entire recruitment pipeline — from resume screening to onboarding — using real AI.

---

## ✨ Features

### 🔐 Authentication & Role-Based Access Control
- Three roles: **Admin**, **Recruiter**, **Candidate**
- Secure password hashing with **bcrypt**
- Session management with role-based navigation
- User registration and profile management

### 📄 AI Resume Screening
- Candidate uploads PDF resume
- Automatic extraction of name, skills, education, experience
- AI-powered match scoring using **Sentence Transformers**
- Semantic similarity — understands meaning, not just keywords
- Displays match percentage, matching skills, and missing skills

### 🎤 AI Interview Analysis
- Candidate uploads audio or video recording
- Speech-to-text transcription using **OpenAI Whisper**
- Transcript analyzed by **GPT-4o-mini**
- Generates Communication Score, Technical Score, Confidence Score
- Provides strengths, weaknesses, and hiring recommendation

### 📊 Recruiter Dashboard
- Real-time KPIs — open jobs, applications, shortlisted, hired
- Plotly charts — application status distribution, applications per job
- Resume match score distribution
- Top candidate rankings

### 🙋 Candidate Dashboard
- Application history and status tracking
- Resume upload and AI parsing
- Interview report and AI feedback
- Profile management

### 🛡️ Admin Dashboard
- Platform-wide analytics
- User management — activate/deactivate accounts
- View all candidates, recruiters, jobs, and applications

### 💼 Job Management
- Create, update, delete job openings
- Search and filter jobs by title or skills
- One-click application for candidates

### 🤖 AI Recommendation Engine
- Ranks all candidates for a job by semantic similarity
- Powered by Sentence Transformers embeddings
- Returns top N candidates with match scores

### 🎉 Onboarding Module
- Offer letter tracking
- Document checklist with progress bar
- Joining status management

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| Database | SQLite |
| AI - Resume Matching | Sentence Transformers (all-MiniLM-L6-v2) |
| AI - Interview Analysis | OpenAI GPT-4o-mini |
| AI - Transcription | OpenAI Whisper |
| Resume Parsing | PyPDF2 |
| Visualization | Plotly, Pandas |
| Security | bcrypt |
| Environment | python-dotenv |

---

## 📁 Project Structure

```
hr_management_system/
├── app.py                    # Main Streamlit entry point
├── config.py                 # App configuration
├── requirements.txt          # Dependencies
├── .env                      # API keys (never commit)
│
├── database/
│   ├── db.py                 # SQLite connection and helpers
│   ├── schema.sql            # 9-table database schema
│   └── hr.db                 # Auto-created on first run
│
├── modules/
│   ├── auth.py               # Authentication & RBAC
│   ├── resume.py             # AI resume screening
│   ├── interview.py          # Whisper + GPT interview analysis
│   ├── jobs.py               # Job management
│   ├── recommendation.py     # AI candidate ranking engine
│   └── onboarding.py         # Onboarding workflow
│
├── dashboards/
│   ├── admin.py              # Admin analytics dashboard
│   ├── recruiter.py          # Recruiter dashboard + charts
│   └── candidate.py          # Candidate dashboard
│
├── utils/
│   ├── pdf_parser.py         # Resume text extraction
│   ├── ai_helpers.py         # OpenAI API wrappers
│   ├── file_handler.py       # File upload management
│   └── validators.py         # Input validation
│
├── models/
│   └── embeddings.py         # Sentence Transformer model loader
│
└── assets/
    └── style.css             # Custom UI styling
```

---

## 🗄️ Database Schema

The system uses **9 tables**:

| Table | Description |
|-------|-------------|
| `users` | All user accounts with roles |
| `candidates` | Candidate profiles |
| `recruiters` | Recruiter profiles |
| `jobs` | Job openings |
| `applications` | Candidate job applications |
| `resume_scores` | AI match scores per application |
| `interviews` | Interview recordings and transcripts |
| `interview_reports` | AI-generated interview analysis |
| `onboarding` | Onboarding status and checklists |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Ekta-13/hr-management-system.git
cd hr-management-system

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Add your OpenAI API key to .env

# 5. Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🔐 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Recruiter | Register via UI | — |
| Candidate | Register via UI | — |

---

## 🧠 How the AI Works

### Resume Match Scoring
1. Candidate uploads PDF resume
2. PyPDF2 extracts raw text
3. `all-MiniLM-L6-v2` Sentence Transformer converts resume and job description into 384-dimensional vectors
4. Cosine similarity is computed between the two vectors
5. Score is normalized to 0–100%

This approach catches semantic matches that keyword matching misses — for example, *"developed REST APIs"* matches *"backend web services"*.

### Interview Analysis
1. Candidate uploads audio/video file
2. OpenAI Whisper transcribes speech to text locally
3. Transcript is sent to GPT-4o-mini with a structured prompt
4. GPT returns JSON with scores and qualitative feedback
5. Results are stored and displayed as radar charts

---

## ☁️ Deployment

### Streamlit Community Cloud (Free)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `OPENAI_API_KEY` in Secrets
5. Deploy!

---

## 🎤 Key Design Decisions

- **Streamlit over FastAPI** — faster to build a working UI for a hackathon without writing HTML/CSS
- **SQLite over PostgreSQL** — zero setup, single file, portable for demos
- **Sentence Transformers over keyword matching** — semantic understanding gives far more accurate resume matching
- **GPT-4o-mini over GPT-4** — same quality for structured JSON at a fraction of the cost
- **bcrypt for passwords** — industry standard, slow by design to resist brute-force attacks

---

## 👩‍💻 Author

**Ekta Gupta**
- GitHub: [@Ekta-13](https://github.com/Ekta-13)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
