# 🧠 AI-Powered HR Management System
> **An Intelligent Recruitment Automation Platform with AI Resume Screening & Interview Analysis**

🔗 [https://hr-management-system-mzdu8heyjr5appqvymdefxf.streamlit.app](#)

## 🎯 What it is
I engineered an end-to-end **AI-Powered HR Management System** that automates the entire recruitment pipeline — from resume screening to onboarding. The system supports three roles: Admin, Recruiter, and Candidate, with a clean role-based dashboard for each.

## ⚙️ How it works
The system follows a complete **AI-driven Recruitment Pipeline**:
1. **Resume Parsing:** Uses **PyPDF2** to extract raw text from uploaded PDFs and identifies skills, education, and experience automatically.
2. **Semantic Matching:** Converts resume and job description into 384-dimensional vectors using **Sentence Transformers (all-MiniLM-L6-v2)** and computes cosine similarity for an AI match score.
3. **Interview Analysis:** Candidate uploads audio/video — **OpenAI Whisper** transcribes it to text, then **GPT-4o-mini** analyzes communication, technical, and confidence scores.
4. **AI Recommendation Engine:** Ranks all candidates for a job by semantic similarity and returns the top matches instantly.

## 🚀 Key Features
- **🤖 AI Resume Screening** — Semantic match scoring, not just keyword matching
- **🎤 AI Interview Analysis** — Whisper transcription + GPT-4o-mini scoring with radar charts
- **📊 Recruiter Dashboard** — Real-time KPIs and Plotly analytics charts
- **🏆 AI Recommendation Engine** — Ranks candidates by semantic similarity
- **🔐 Role-Based Access** — Separate dashboards for Admin, Recruiter, and Candidate
- **🎉 Onboarding Module** — Offer tracking, document checklist, joining status

## 🛠️ Tech Stack
- **Frontend** — Streamlit
- **Backend** — Python (Modular Architecture)
- **Database** — SQLite (9 tables)
- **AI / NLP** — Sentence Transformers, OpenAI Whisper, GPT-4o-mini
- **Resume Parsing** — PyPDF2
- **Visualization** — Plotly, Pandas
- **Security** — bcrypt password hashing

## 🧠 Strategic Engineering
- **Semantic Matching over Keywords** — Sentence Transformers understand context, so *"developed REST APIs"* correctly matches *"backend web services"*
- **Local Transcription** — Whisper runs locally, keeping interview data private
- **RBAC Security** — Every route is guarded by role checks; unauthorized access is blocked at the module level
- **Modular Architecture** — Each feature (auth, resume, interview, jobs, onboarding) is an independent Python module

## ⚡ Quick Start
```bash
# Clone the repository
git clone https://github.com/Ekta-13/hr-management-system.git

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🔐 Demo Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Recruiter | Register via UI | — |
| Candidate | Register via UI | — |

## 👩‍💻 Author
**Ekta Gupta** — [@Ekta-13](https://github.com/Ekta-13)
