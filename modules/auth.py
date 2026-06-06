"""
modules/auth.py — Login, registration, session management, and RBAC
"""
import streamlit as st
from database import db
from utils.validators import is_valid_email, is_valid_password, is_valid_username
from config import ROLE_ADMIN, ROLE_RECRUITER, ROLE_CANDIDATE


def init_session():
    for key in ["logged_in", "user", "role", "candidate_profile", "recruiter_profile"]:
        if key not in st.session_state:
            st.session_state[key] = None if key not in ["logged_in"] else False


def login(username: str, password: str) -> tuple[bool, str]:
    user = db.verify_user(username, password)
    if not user:
        return False, "Invalid username or password."
    st.session_state.logged_in = True
    st.session_state.user = user
    st.session_state.role = user["role"]
    if user["role"] == ROLE_CANDIDATE:
        st.session_state.candidate_profile = db.get_candidate_by_user(user["id"])
    elif user["role"] == ROLE_RECRUITER:
        st.session_state.recruiter_profile = db.get_recruiter_by_user(user["id"])
    return True, "Login successful!"


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def register_user(username, email, password, role, full_name, department=""):
    ok, msg = is_valid_username(username)
    if not ok:
        return False, msg
    if not is_valid_email(email):
        return False, "Invalid email address."
    ok, msg = is_valid_password(password)
    if not ok:
        return False, msg
    existing = db.fetchone("SELECT id FROM users WHERE username=? OR email=?", (username, email))
    if existing:
        return False, "Username or email already exists."
    try:
        user_id = db.create_user(username, email, password, role)
        if role == ROLE_CANDIDATE:
            db.create_candidate_profile(user_id, full_name)
        elif role == ROLE_RECRUITER:
            db.create_recruiter_profile(user_id, full_name, department)
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Registration failed: {e}"


def require_role(*roles):
    """Guard: redirect to login if not authenticated or wrong role."""
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to continue.")
        st.stop()
    if st.session_state.get("role") not in roles:
        st.error("Access denied. Insufficient permissions.")
        st.stop()


def render_login_page():
    st.markdown("<h2 style='text-align:center;'>🧠 AI HR Management System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Automate recruitment with AI</p>", unsafe_allow_html=True)
    st.divider()

    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form"):
            st.subheader("Sign In")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, msg = login(username, password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.info("**Demo Credentials:**\nAdmin: `admin` / `admin123`\nCreate recruiter/candidate accounts via Register tab.")

    with tab_register:
        with st.form("register_form"):
            st.subheader("Create Account")
            col1, col2 = st.columns(2)
            with col1:
                reg_username = st.text_input("Username*")
                reg_email = st.text_input("Email*")
                reg_password = st.text_input("Password*", type="password")
            with col2:
                reg_full_name = st.text_input("Full Name*")
                reg_role = st.selectbox("Account Type", ["candidate", "recruiter"])
                reg_department = st.text_input("Department (recruiters only)")

            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not all([reg_username, reg_email, reg_password, reg_full_name]):
                    st.error("Please fill in all required fields.")
                else:
                    ok, msg = register_user(reg_username, reg_email, reg_password, reg_role, reg_full_name, reg_department)
                    if ok:
                        st.success(msg + " Please log in.")
                    else:
                        st.error(msg)
