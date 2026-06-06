"""
modules/recommendation.py — AI candidate recommendation engine using Sentence Transformers
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database import db
from models.embeddings import compute_match_score


def recommend_candidates_for_job(job_id: int, top_n: int = 5) -> list:
    """Rank all applicants for a job by semantic similarity."""
    job = db.get_job_by_id(job_id)
    if not job:
        return []

    jd_text = f"{job['title']} {job['description']} {job['required_skills']}"
    applications = db.get_applications_for_job(job_id)

    scored = []
    for app in applications:
        candidate = db.get_candidate_by_id(app["candidate_id"])
        resume_text = f"{candidate.get('skills', '')} {candidate.get('education', '')} {candidate.get('full_name', '')}"

        if candidate.get("resume_path"):
            try:
                with open(candidate["resume_path"], "rb") as f:
                    from utils.pdf_parser import extract_text_from_pdf
                    text = extract_text_from_pdf(f.read())
                    if text:
                        resume_text = text
            except Exception:
                pass

        score = compute_match_score(resume_text, jd_text)
        scored.append({
            "candidate_id": app["candidate_id"],
            "app_id": app["id"],
            "full_name": candidate.get("full_name", "Unknown"),
            "skills": candidate.get("skills", ""),
            "experience_years": candidate.get("experience_years", 0),
            "status": app["status"],
            "match_score": score,
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:top_n]


def render_recommendation_engine():
    st.subheader("🤖 AI Candidate Recommendation Engine")
    st.markdown("*Powered by Sentence Transformers — semantic matching, not just keyword search*")

    jobs = db.get_all_jobs(status="open")
    if not jobs:
        st.info("No open jobs available.")
        return

    job_options = {f"[{j['id']}] {j['title']}": j["id"] for j in jobs}
    col1, col2 = st.columns([3, 1])
    with col1:
        sel = st.selectbox("Select job to find top candidates", list(job_options.keys()))
    with col2:
        top_n = st.number_input("Top N", 3, 20, 5)

    job_id = job_options[sel]

    if st.button("🔍 Find Best Matches", use_container_width=True):
        with st.spinner("Computing semantic similarity scores…"):
            recommendations = recommend_candidates_for_job(job_id, top_n)

        if not recommendations:
            st.warning("No applicants found for this job.")
            return

        st.markdown(f"### Top {len(recommendations)} Recommended Candidates")

        df = pd.DataFrame([{
            "Rank": i + 1,
            "Candidate": r["full_name"],
            "Match Score": r["match_score"],
            "Experience": f"{r['experience_years']} yrs",
            "Skills Preview": (r["skills"] or "")[:80] + "…",
            "Status": r["status"],
        } for i, r in enumerate(recommendations)])

        # Horizontal bar chart
        fig = px.bar(
            df, x="Match Score", y="Candidate", orientation="h",
            color="Match Score",
            color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
            title="Semantic Match Scores",
            range_x=[0, 100],
        )
        fig.update_layout(height=300, showlegend=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Quick shortlist top candidate
        if recommendations:
            top = recommendations[0]
            st.markdown(f"**💡 Top pick:** {top['full_name']} with {top['match_score']:.1f}% match")
            if st.button(f"✅ Shortlist {top['full_name']}", use_container_width=True):
                db.update_application_status(top["app_id"], "shortlisted")
                st.success("Shortlisted!")
                st.rerun()
