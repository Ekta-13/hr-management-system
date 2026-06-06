"""
dashboards/admin.py — Admin dashboard: platform analytics, user management
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database import db
from utils.validators import is_valid_email


def render_admin_dashboard():
    st.markdown("### 🛡️ Admin Control Panel")
    st.divider()

    stats = db.get_platform_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Users", stats["total_users"])
    c2.metric("Candidates", stats["total_candidates"])
    c3.metric("Recruiters", stats["total_recruiters"])
    c4.metric("Total Jobs", stats["total_jobs"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Open Jobs", stats["open_jobs"])
    c6.metric("Applications", stats["total_applications"])
    c7.metric("Hired", stats["hired"])
    c8.metric("Interviews Done", stats["interviews_completed"])

    st.divider()

    tab_users, tab_candidates, tab_recruiters, tab_jobs, tab_apps = st.tabs(
        ["👥 Users", "🙋 Candidates", "💼 Recruiters", "📋 Jobs", "📄 Applications"]
    )

    with tab_users:
        st.markdown("### All Users")
        users = db.get_all_users()
        if users:
            df = pd.DataFrame(users)
            df["is_active"] = df["is_active"].map({1: "✅ Active", 0: "❌ Inactive"})
            st.dataframe(df[["id", "username", "email", "role", "is_active", "created_at"]],
                         use_container_width=True, hide_index=True)

            st.markdown("#### Toggle User Status")
            uid = st.number_input("User ID to toggle", min_value=1, step=1)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Activate User"):
                    db.toggle_user_active(uid, 1)
                    st.success(f"User {uid} activated.")
                    st.rerun()
            with col2:
                if st.button("❌ Deactivate User"):
                    db.toggle_user_active(uid, 0)
                    st.warning(f"User {uid} deactivated.")
                    st.rerun()

    with tab_candidates:
        candidates = db.get_all_candidates()
        if candidates:
            df = pd.DataFrame(candidates)
            st.dataframe(
                df[["id", "full_name", "email", "skills", "experience_years", "status", "created_at"]],
                use_container_width=True, hide_index=True
            )

            # Status chart
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig = px.pie(status_counts, names="Status", values="Count",
                         title="Candidate Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No candidates registered yet.")

    with tab_recruiters:
        recruiters = db.get_all_recruiters()
        if recruiters:
            df = pd.DataFrame(recruiters)
            st.dataframe(df[["id", "full_name", "email", "department", "created_at"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No recruiters registered yet.")

    with tab_jobs:
        jobs = db.get_all_jobs()
        if jobs:
            df = pd.DataFrame(jobs)
            st.dataframe(
                df[["id", "title", "location", "job_type", "status", "experience_required", "created_at"]],
                use_container_width=True, hide_index=True
            )
            fig = px.bar(
                df.groupby("status").size().reset_index(name="Count"),
                x="status", y="Count", title="Jobs by Status",
                color="status",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No jobs created yet.")

    with tab_apps:
        applications = db.get_all_applications()
        if applications:
            df = pd.DataFrame(applications)
            st.dataframe(
                df[["id", "full_name", "job_title", "status", "applied_at"]],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No applications yet.")
