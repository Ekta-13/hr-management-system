"""
dashboards/candidate.py — Candidate profile and application tracking dashboard
"""
import streamlit as st
from database import db


def render_candidate_dashboard(candidate_id: int):
    candidate = db.get_candidate_by_id(candidate_id)
    if not candidate:
        st.error("Candidate profile not found.")
        return

    st.markdown(f"### 👋 Hello, {candidate['full_name']}")
    st.divider()

    applications = db.get_applications_for_candidate(candidate_id)
    total = len(applications)
    shortlisted = sum(1 for a in applications if a["status"] == "shortlisted")
    in_interview = sum(1 for a in applications if a["status"] == "interview")
    offers = sum(1 for a in applications if a["status"] in ("offered", "hired"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Applications", total)
    c2.metric("Shortlisted", shortlisted)
    c3.metric("Interviews", in_interview)
    c4.metric("Offers", offers)

    # Resume status
    st.divider()
    if candidate.get("resume_path"):
        st.success("✅ Resume uploaded")
        st.markdown(f"**Skills on file:** {candidate.get('skills', 'None parsed')}")
        st.markdown(f"**Education:** {candidate.get('education', 'Not set')}")
        st.markdown(f"**Experience:** {candidate.get('experience_years', 0)} years")
    else:
        st.warning("⚠️ No resume uploaded. Upload your resume to start applying!")

    # Application history
    st.markdown("### 📋 Application History")
    if not applications:
        st.info("You haven't applied to any jobs yet. Browse open jobs to get started!")
    else:
        status_emoji = {
            "pending": "⏳", "screening": "🔍", "shortlisted": "⭐",
            "interview": "🎤", "offered": "🎉", "hired": "✅", "rejected": "❌",
        }
        for app in applications:
            icon = status_emoji.get(app["status"], "•")
            with st.expander(f"{icon} {app['job_title']} | Status: {app['status'].title()}"):
                col1, col2 = st.columns(2)
                col1.write(f"**Applied:** {app['applied_at'][:10]}")
                col2.write(f"**Location:** {app.get('location', 'N/A')}")

                rs = db.get_resume_score(app["id"])
                if rs:
                    score = rs["match_score"]
                    color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
                    st.metric("Resume Match Score", f"{color} {score:.1f}%")
                    if rs.get("ai_summary"):
                        st.info(f"💡 AI Feedback: {rs['ai_summary']}")

                interview = db.get_interview_by_application(app["id"])
                if interview and interview["status"] == "completed":
                    report = db.get_interview_report(interview["id"])
                    if report:
                        st.markdown("**🎤 Interview Score**")
                        ic1, ic2, ic3 = st.columns(3)
                        ic1.metric("Communication", f"{report['communication_score']}/10")
                        ic2.metric("Technical", f"{report['technical_score']}/10")
                        ic3.metric("Overall", f"{report['overall_score']}/10")


def render_profile_editor(candidate_id: int, user_id: int):
    st.subheader("✏️ Edit Profile")
    candidate = db.get_candidate_by_id(candidate_id)
    user = db.get_user_by_id(user_id)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", candidate.get("full_name", ""))
            phone = st.text_input("Phone", candidate.get("phone", ""))
        with col2:
            location = st.text_input("Location", candidate.get("location", ""))
            linkedin = st.text_input("LinkedIn URL", candidate.get("linkedin_url", ""))

        skills = st.text_area("Skills (comma-separated)", candidate.get("skills", ""), height=80)
        education = st.text_area("Education", candidate.get("education", ""), height=60)
        experience_years = st.number_input("Years of Experience", 0, 50, int(candidate.get("experience_years") or 0))

        if st.form_submit_button("💾 Save Profile", use_container_width=True):
            db.update_candidate(candidate_id,
                                full_name=full_name, phone=phone, location=location,
                                linkedin_url=linkedin, skills=skills, education=education,
                                experience_years=experience_years)
            st.success("Profile updated!")
            st.rerun()
