"""
modules/resume.py — Resume upload, parsing, AI match scoring with Sentence Transformers
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from database import db
from utils.pdf_parser import parse_resume
from utils.file_handler import save_resume
from utils.ai_helpers import generate_resume_summary
from models.embeddings import compute_match_score
from config import SCORE_EXCELLENT, SCORE_GOOD


def _score_color(score):
    if score >= SCORE_EXCELLENT:
        return "🟢"
    elif score >= SCORE_GOOD:
        return "🟡"
    return "🔴"


def render_resume_upload(candidate_id: int):
    """Candidate-side: upload and view parsed resume."""
    st.subheader("📄 Resume Upload")
    candidate = db.get_candidate_by_id(candidate_id)

    if candidate and candidate.get("resume_path"):
        st.success("✅ Resume on file. Upload a new one to replace it.")

    uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    if uploaded:
        file_bytes = uploaded.read()
        with st.spinner("Parsing resume…"):
            parsed = parse_resume(file_bytes)

        if "error" in parsed:
            st.error(parsed["error"])
            return

        st.markdown("### Parsed Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {parsed['name']}")
            st.write(f"**Email:** {parsed['email']}")
            st.write(f"**Phone:** {parsed['phone']}")
            st.write(f"**Experience:** {parsed['experience_years']} years")
        with col2:
            st.write(f"**Education:** {parsed['education']}")
            st.markdown(f"**Skills detected ({len(parsed['skills'])}):**")
            if parsed["skills"]:
                st.write(", ".join(f"`{s}`" for s in sorted(parsed["skills"])))

        if st.button("💾 Save Resume to Profile", use_container_width=True):
            path = save_resume(file_bytes, uploaded.name, candidate_id)
            skills_str = ", ".join(parsed["skills"])
            db.update_candidate(
                candidate_id,
                resume_path=path,
                skills=skills_str,
                education=parsed["education"],
                experience_years=parsed["experience_years"],
            )
            st.success("Resume saved successfully!")
            st.rerun()


def render_resume_screener_recruiter():
    """Recruiter-side: score a resume against a job description."""
    st.subheader("🔍 AI Resume Screener")

    jobs = db.get_all_jobs(status="open")
    if not jobs:
        st.info("No open jobs. Create a job first.")
        return

    job_options = {f"[{j['id']}] {j['title']}": j for j in jobs}
    selected_job_key = st.selectbox("Select Job", list(job_options.keys()))
    selected_job = job_options[selected_job_key]

    st.markdown(f"**Required Skills:** `{selected_job['required_skills']}`")

    applications = db.get_applications_for_job(selected_job["id"])
    if not applications:
        st.info("No applications for this job yet.")
        return

    st.markdown(f"### {len(applications)} Applicants — Score All")

    if st.button("🤖 Run AI Scoring on All Applicants", use_container_width=True):
        jd_text = f"{selected_job['title']} {selected_job['description']} {selected_job['required_skills']}"
        progress = st.progress(0)
        for i, app in enumerate(applications):
            candidate = db.get_candidate_by_id(app["candidate_id"])
            resume_text = f"{candidate.get('skills','')} {candidate.get('education','')} {candidate.get('full_name','')}"

            # Try to read actual resume text if available
            if candidate.get("resume_path"):
                try:
                    with open(candidate["resume_path"], "rb") as f:
                        from utils.pdf_parser import extract_text_from_pdf
                        resume_text = extract_text_from_pdf(f.read()) or resume_text
                except Exception:
                    pass

            match_score = compute_match_score(resume_text, jd_text)

            # Compute matching / missing skills
            job_skills = [s.strip().lower() for s in selected_job["required_skills"].split(",") if s.strip()]
            candidate_skills = [s.strip().lower() for s in candidate.get("skills", "").split(",") if s.strip()]
            matching = [s for s in job_skills if any(s in cs for cs in candidate_skills)]
            missing = [s for s in job_skills if s not in matching]

            ai_summary = generate_resume_summary(resume_text, jd_text)

            db.save_resume_score(
                app["id"],
                match_score,
                ", ".join(matching),
                ", ".join(missing),
                ai_summary,
            )
            progress.progress((i + 1) / len(applications))

        st.success("✅ All applicants scored!")
        st.rerun()

    # Show ranked results
    ranked = db.get_top_candidates_for_job(selected_job["id"])
    if ranked:
        st.markdown("### 🏆 Candidate Rankings")
        df_data = []
        for r in ranked:
            score = r.get("match_score") or 0
            df_data.append({
                "Rank": len(df_data) + 1,
                "Candidate": r["full_name"],
                "Match %": f"{score:.1f}%",
                "Score": score,
                "Matching Skills": r.get("matching_skills") or "—",
                "Missing Skills": r.get("missing_skills") or "—",
                "Status": r["status"],
                "Indicator": _score_color(score),
            })

        df = pd.DataFrame(df_data)

        # Bar chart
        fig = px.bar(
            df, x="Candidate", y="Score",
            color="Score",
            color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
            title="Resume Match Scores",
            labels={"Score": "Match Score (%)"},
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

        # Table
        display_df = df[["Rank", "Indicator", "Candidate", "Match %", "Matching Skills", "Missing Skills", "Status"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        app_options = {f"{r['full_name']} ({(r.get('match_score') or 0):.1f}%)": r["app_id"] for r in ranked}
        sel = st.selectbox("Select candidate", list(app_options.keys()))
        app_id = app_options[sel]
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Shortlist", use_container_width=True):
                db.update_application_status(app_id, "shortlisted")
                st.success("Shortlisted!")
                st.rerun()
        with col2:
            if st.button("🎤 Move to Interview", use_container_width=True):
                db.update_application_status(app_id, "interview")
                db.create_interview(app_id)
                st.success("Moved to interview stage!")
                st.rerun()
        with col3:
            if st.button("❌ Reject", use_container_width=True):
                db.update_application_status(app_id, "rejected")
                st.warning("Rejected.")
                st.rerun()
