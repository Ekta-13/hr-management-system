"""
app.py — Main entry point for the AI-Powered HR Management System
Run with: streamlit run app.py
"""
import streamlit as st
from pathlib import Path

# ── Page config (MUST be first Streamlit call) ─────────────────
st.set_page_config(
    page_title="AI HR Management System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load custom CSS ────────────────────────────────────────────
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Force light theme fixes ────────────────────────────────────
st.markdown("""
<style>
/* ── Page background ── */
.stApp { background-color: #f0f4ff !important; }

/* ── ALL buttons: always white text on indigo ── */
.stButton > button,
.stButton > button:link,
.stButton > button:visited,
.stButton > button:hover,
.stButton > button:active,
.stButton > button:focus,
button[kind="primary"],
button[kind="secondary"],
div[data-testid="stFormSubmitButton"] > button {
    background-color: #4f46e5 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 10px 20px !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.3) !important;
}
.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #4338ca !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(79,70,229,0.45) !important;
}

/* ── Input fields ── */
input, textarea {
    background-color: #ffffff !important;
    color: #1e1b4b !important;
    border: 1.5px solid #c7d2fe !important;
    border-radius: 8px !important;
}
input::placeholder, textarea::placeholder {
    color: #a5b4fc !important;
}

/* ── Input labels ── */
label,
.stTextInput label,
.stSelectbox label,
.stTextArea label,
.stNumberInput label,
.stFileUploader label,
p {
    color: #1e1b4b !important;
    font-weight: 500 !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    color: #1e1b4b !important;
    font-weight: 700 !important;
}

/* ── Form container ── */
.stForm {
    background: #ffffff !important;
    padding: 24px !important;
    border-radius: 14px !important;
    border: 1px solid #e0e7ff !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.08) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    color: #4f46e5 !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: #3730a3 !important;
    border-bottom: 3px solid #4f46e5 !important;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid #c7d2fe !important;
    box-shadow: 0 2px 6px rgba(99,102,241,0.1) !important;
}
div[data-testid="stMetricLabel"] { color: #6366f1 !important; font-weight: 600 !important; }
div[data-testid="stMetricValue"] { color: #1e1b4b !important; font-weight: 800 !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important;
}
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #e0e7ff !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #ef4444 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #dc2626 !important;
}

/* ── Alerts ── */
div[data-testid="stNotification"],
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 10px !important;
}
.stSuccess { background-color: #dcfce7 !important; color: #14532d !important; }
.stWarning { background-color: #fef9c3 !important; color: #713f12 !important; }
.stError   { background-color: #fee2e2 !important; color: #7f1d1d !important; }
.stInfo    { background-color: #e0e7ff !important; color: #1e1b4b !important; }

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1.5px solid #c7d2fe !important;
    border-radius: 8px !important;
    color: #1e1b4b !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 10px !important;
    border: 1px solid #c7d2fe !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #ffffff !important;
    color: #1e1b4b !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: 1px solid #e0e7ff !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Init DB & session ──────────────────────────────────────────
from database.db import init_db
init_db()

from modules.auth import init_session, render_login_page, logout
init_session()

# ── Show login if not authenticated ───────────────────────────
if not st.session_state.get("logged_in"):
    render_login_page()
    st.stop()

# ── Imports after auth ─────────────────────────────────────────
from config import ROLE_ADMIN, ROLE_RECRUITER, ROLE_CANDIDATE
from database import db

user = st.session_state.user
role = st.session_state.role

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 🧠 AI HR System")
    st.markdown(f"**{user['username']}** | `{role.upper()}`")
    st.divider()

    if role == ROLE_ADMIN:
        nav = st.radio("Navigation", [
            "📊 Dashboard",
            "💼 Job Management",
            "👥 User Management",
        ])
    elif role == ROLE_RECRUITER:
        nav = st.radio("Navigation", [
            "📊 Dashboard",
            "💼 Job Management",
            "🔍 Resume Screener",
            "🤖 AI Recommendations",
            "🎤 Interview Analysis",
            "🎉 Onboarding",
        ])
    elif role == ROLE_CANDIDATE:
        nav = st.radio("Navigation", [
            "📊 My Dashboard",
            "📄 My Resume",
            "🔍 Browse Jobs",
            "🎤 My Interview",
            "🎉 Onboarding",
            "✏️ Edit Profile",
        ])

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# ── ADMIN ROUTES ───────────────────────────────────────────────
if role == ROLE_ADMIN:
    from dashboards.admin import render_admin_dashboard
    from modules.jobs import render_job_management

    if nav == "📊 Dashboard":
        render_admin_dashboard()
    elif nav == "💼 Job Management":
        render_job_management(recruiter_id=None, is_admin=True)
    elif nav == "👥 User Management":
        render_admin_dashboard()

# ── RECRUITER ROUTES ───────────────────────────────────────────
elif role == ROLE_RECRUITER:
    recruiter_profile = st.session_state.get("recruiter_profile")
    if not recruiter_profile:
        recruiter_profile = db.get_recruiter_by_user(user["id"])
        st.session_state.recruiter_profile = recruiter_profile

    if not recruiter_profile:
        st.error("Recruiter profile not found. Contact admin.")
        st.stop()

    recruiter_id = recruiter_profile["id"]

    from dashboards.recruiter import render_recruiter_dashboard
    from modules.jobs import render_job_management
    from modules.resume import render_resume_screener_recruiter
    from modules.recommendation import render_recommendation_engine
    from modules.interview import render_interview_analysis_recruiter
    from modules.onboarding import render_onboarding_recruiter

    if nav == "📊 Dashboard":
        render_recruiter_dashboard(recruiter_id)
    elif nav == "💼 Job Management":
        render_job_management(recruiter_id=recruiter_id)
    elif nav == "🔍 Resume Screener":
        render_resume_screener_recruiter()
    elif nav == "🤖 AI Recommendations":
        render_recommendation_engine()
    elif nav == "🎤 Interview Analysis":
        render_interview_analysis_recruiter()
    elif nav == "🎉 Onboarding":
        render_onboarding_recruiter()

# ── CANDIDATE ROUTES ───────────────────────────────────────────
elif role == ROLE_CANDIDATE:
    candidate_profile = st.session_state.get("candidate_profile")
    if not candidate_profile:
        candidate_profile = db.get_candidate_by_user(user["id"])
        st.session_state.candidate_profile = candidate_profile

    if not candidate_profile:
        st.error("Candidate profile not found. Contact admin.")
        st.stop()

    candidate_id = candidate_profile["id"]

    from dashboards.candidate import render_candidate_dashboard, render_profile_editor
    from modules.resume import render_resume_upload
    from modules.jobs import render_candidate_job_browser
    from modules.interview import render_interview_upload_candidate
    from modules.onboarding import render_onboarding_candidate

    if nav == "📊 My Dashboard":
        render_candidate_dashboard(candidate_id)
    elif nav == "📄 My Resume":
        render_resume_upload(candidate_id)
    elif nav == "🔍 Browse Jobs":
        render_candidate_job_browser(candidate_id)
    elif nav == "🎤 My Interview":
        render_interview_upload_candidate(candidate_id)
    elif nav == "🎉 Onboarding":
        render_onboarding_candidate(candidate_id)
    elif nav == "✏️ Edit Profile":
        render_profile_editor(candidate_id, user["id"])