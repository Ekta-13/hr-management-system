"""
dashboards/recruiter.py — Recruiter dashboard with analytics and charts
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import db


def render_recruiter_dashboard(recruiter_id: int):
    recruiter = db.get_recruiter_by_id(recruiter_id) if hasattr(db, 'get_recruiter_by_id') else db.fetchone("SELECT * FROM recruiters WHERE id=?", (recruiter_id,))
    name = recruiter["full_name"] if recruiter else "Recruiter"
    st.markdown(f"### 👋 Welcome back, {name}")
    st.divider()

    # ── KPI Cards ──────────────────────────────────────────────
    jobs = db.get_jobs_by_recruiter(recruiter_id)
    job_ids = [j["id"] for j in jobs]

    all_apps = []
    for jid in job_ids:
        all_apps.extend(db.get_applications_for_job(jid))

    total_apps = len(all_apps)
    shortlisted = sum(1 for a in all_apps if a["status"] == "shortlisted")
    in_interview = sum(1 for a in all_apps if a["status"] == "interview")
    rejected = sum(1 for a in all_apps if a["status"] == "rejected")
    hired = sum(1 for a in all_apps if a["status"] == "hired")
    open_jobs = sum(1 for j in jobs if j["status"] == "open")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Open Jobs", open_jobs)
    c2.metric("Total Applications", total_apps)
    c3.metric("Shortlisted", shortlisted)
    c4.metric("In Interview", in_interview)
    c5.metric("Hired", hired)
    c6.metric("Rejected", rejected)

    if total_apps == 0:
        st.info("No applications yet. Post a job and start screening!")
        return

    st.divider()

    # ── Charts ─────────────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        status_counts = {}
        for a in all_apps:
            status_counts[a["status"]] = status_counts.get(a["status"], 0) + 1
        df_status = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
        fig_pie = px.pie(df_status, names="Status", values="Count",
                         title="Application Status Distribution",
                         color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_layout(height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        job_app_counts = []
        for j in jobs:
            apps = db.get_applications_for_job(j["id"])
            job_app_counts.append({"Job": j["title"][:30], "Applications": len(apps)})
        df_jobs = pd.DataFrame(job_app_counts)
        fig_bar = px.bar(df_jobs, x="Job", y="Applications",
                         title="Applications per Job",
                         color="Applications",
                         color_continuous_scale="blues")
        fig_bar.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Resume Score Distribution ──────────────────────────────
    st.markdown("### 📊 Resume Match Score Distribution")
    score_data = []
    for app in all_apps:
        rs = db.get_resume_score(app["id"])
        if rs:
            score_data.append({
                "Candidate": app.get("full_name", "Unknown"),
                "Score": rs["match_score"],
                "Job": app.get("job_title", ""),
            })

    if score_data:
        df_scores = pd.DataFrame(score_data)
        fig_hist = px.histogram(df_scores, x="Score", nbins=10,
                                title="Resume Match Score Distribution",
                                color_discrete_sequence=["#6366f1"])
        fig_hist.update_layout(height=280)
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("### 🏆 Top Scored Candidates")
        df_top = df_scores.sort_values("Score", ascending=False).head(10)
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("Run AI scoring on your candidates to see score distributions.")
