"""
modules/jobs.py — Job creation, editing, deletion, and applicant management
"""
import streamlit as st
from database import db


def render_job_management(recruiter_id: int = None, is_admin: bool = False):
    st.subheader("💼 Job Management")
    tab_list, tab_create = st.tabs(["📋 All Jobs", "➕ Create Job"])

    with tab_list:
        jobs = db.get_all_jobs() if is_admin else db.get_jobs_by_recruiter(recruiter_id)
        if not jobs:
            st.info("No jobs found. Create one in the next tab.")
        else:
            for job in jobs:
                status_icon = {"open": "🟢", "closed": "🔴", "draft": "🟡"}.get(job["status"], "⚪")
                with st.expander(f"{status_icon} [{job['id']}] {job['title']} — {job.get('location','Remote')}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Type:** {job['job_type']} | **Experience:** {job['experience_required']}+ yrs | **Salary:** {job.get('salary_range','N/A')}")
                        st.markdown(f"**Required Skills:** `{job['required_skills']}`")
                        st.markdown(f"**Description:**\n{job['description'][:400]}…")
                    with col2:
                        st.markdown(f"**Status:** {job['status']}")
                        new_status = st.selectbox("Change status", ["open", "closed", "draft"],
                                                  index=["open", "closed", "draft"].index(job["status"]),
                                                  key=f"status_{job['id']}")
                        if st.button("Update", key=f"upd_{job['id']}"):
                            db.update_job(job["id"], status=new_status)
                            st.success("Updated!")
                            st.rerun()
                        if st.button("🗑️ Delete", key=f"del_{job['id']}"):
                            db.delete_job(job["id"])
                            st.warning("Job deleted.")
                            st.rerun()

                    # Applicant count
                    apps = db.get_applications_for_job(job["id"])
                    st.markdown(f"**Applicants:** {len(apps)}")
                    if apps:
                        import pandas as pd
                        df = pd.DataFrame([{
                            "Candidate": a["full_name"],
                            "Status": a["status"],
                            "Applied": a["applied_at"][:10],
                        } for a in apps])
                        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_create:
        with st.form("create_job_form"):
            st.subheader("Post a New Job")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Job Title*")
                location = st.text_input("Location", "Remote")
                job_type = st.selectbox("Job Type", ["full-time", "part-time", "contract", "internship"])
            with col2:
                experience_required = st.number_input("Min. Experience (years)", 0, 20, 0)
                salary_range = st.text_input("Salary Range", "Competitive")
                status = st.selectbox("Initial Status", ["open", "draft"])

            description = st.text_area("Job Description*", height=120)
            required_skills = st.text_input("Required Skills* (comma-separated)", "python, sql, communication")

            submitted = st.form_submit_button("📢 Post Job", use_container_width=True)
            if submitted:
                if not title or not description or not required_skills:
                    st.error("Title, description, and skills are required.")
                else:
                    db.create_job(
                        recruiter_id, title, description, required_skills,
                        location, job_type, experience_required, salary_range
                    )
                    db.execute(f"UPDATE jobs SET status=? WHERE id=(SELECT MAX(id) FROM jobs)", (status,))
                    st.success(f"Job '{title}' posted successfully!")
                    st.rerun()


def render_candidate_job_browser(candidate_id: int):
    st.subheader("🔍 Browse & Apply to Jobs")
    jobs = db.get_all_jobs(status="open")

    if not jobs:
        st.info("No open positions at the moment. Check back soon!")
        return

    # Get existing applications to avoid duplicates
    existing_apps = db.get_applications_for_candidate(candidate_id)
    applied_job_ids = {a["job_id"] for a in existing_apps}

    search = st.text_input("🔎 Search by title or skills", "")
    filtered = jobs
    if search:
        q = search.lower()
        filtered = [j for j in jobs if q in j["title"].lower() or q in (j["required_skills"] or "").lower()]

    st.markdown(f"**{len(filtered)} open position(s) found**")

    for job in filtered:
        with st.expander(f"💼 {job['title']} — {job.get('location', 'Remote')}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Type:** {job['job_type']} | **Experience:** {job['experience_required']}+ yrs")
                st.markdown(f"**Salary:** {job.get('salary_range', 'N/A')}")
                st.markdown(f"**Skills:** `{job['required_skills']}`")
                st.markdown(job["description"][:500])
            with col2:
                if job["id"] in applied_job_ids:
                    st.success("✅ Applied")
                else:
                    cover = st.text_area("Cover letter (optional)", key=f"cover_{job['id']}", height=80)
                    if st.button("📨 Apply Now", key=f"apply_{job['id']}", use_container_width=True):
                        candidate = db.get_candidate_by_id(candidate_id)
                        if not candidate or not candidate.get("resume_path"):
                            st.error("Please upload your resume before applying!")
                        else:
                            db.create_application(candidate_id, job["id"], cover)
                            st.success("Application submitted!")
                            st.rerun()
