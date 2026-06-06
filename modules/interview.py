"""
modules/interview.py — Whisper transcription + OpenAI GPT interview analysis
"""
import streamlit as st
import plotly.graph_objects as go
from database import db
from utils.file_handler import save_interview_media
from utils.ai_helpers import analyze_interview_transcript
from config import WHISPER_MODEL


def transcribe_audio(file_path: str) -> str:
    """Transcribe audio/video using OpenAI Whisper."""
    try:
        import whisper
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        return f"[Transcription failed: {e}. Using mock transcript for demo.]"


def _radar_chart(comm, tech, conf):
    categories = ["Communication", "Technical", "Confidence"]
    scores = [comm, tech, conf]
    fig = go.Figure(data=go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(99,102,241,0.25)",
        line=dict(color="#6366f1", width=2),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        height=320,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def render_interview_upload_candidate(candidate_id: int):
    """Candidate uploads interview recording."""
    st.subheader("🎤 Interview Recording Upload")

    candidate = db.get_candidate_by_id(candidate_id)
    applications = db.get_applications_for_candidate(candidate_id)
    interview_apps = [a for a in applications if a["status"] in ("interview", "shortlisted")]

    if not interview_apps:
        st.info("You have no active interview invitations.")
        return

    app_options = {f"{a['job_title']} (Applied: {a['applied_at'][:10]})": a["id"] for a in interview_apps}
    selected_key = st.selectbox("Select Job Application", list(app_options.keys()))
    app_id = app_options[selected_key]

    existing = db.get_interview_by_application(app_id)
    if existing and existing["status"] == "completed":
        st.success("✅ Interview already analyzed. View your report below.")
        _render_candidate_report(existing["id"])
        return

    uploaded = st.file_uploader(
        "Upload interview audio or video",
        type=["mp3", "mp4", "wav", "m4a", "webm", "ogg"],
        help="Record yourself answering interview questions and upload here.",
    )

    if uploaded:
        st.audio(uploaded) if uploaded.type.startswith("audio") else st.video(uploaded)
        if st.button("🚀 Submit for AI Analysis", use_container_width=True):
            file_bytes = uploaded.read()
            with st.spinner("Saving file…"):
                path = save_interview_media(file_bytes, uploaded.name, app_id)

            interview_id = db.create_interview(app_id)
            db.update_interview(interview_id, media_path=path, status="processing")

            with st.spinner("🎙️ Transcribing audio (this may take a minute)…"):
                transcript = transcribe_audio(path)

            with st.spinner("🧠 Analyzing with AI…"):
                job_app = db.get_application_by_id(app_id)
                job = db.get_job_by_id(job_app["job_id"]) if job_app else {}
                analysis = analyze_interview_transcript(transcript, job.get("title", ""))

            db.update_interview(interview_id, transcript=transcript, status="completed")
            db.save_interview_report(
                interview_id,
                analysis.get("communication_score", 0),
                analysis.get("technical_score", 0),
                analysis.get("confidence_score", 0),
                str(analysis.get("strengths", [])),
                str(analysis.get("weaknesses", [])),
                analysis.get("recommendation", "consider"),
                analysis.get("detailed_feedback", ""),
            )
            st.success("✅ Analysis complete!")
            st.rerun()


def _render_candidate_report(interview_id: int):
    report = db.get_interview_report(interview_id)
    if not report:
        st.info("Report not yet available.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Communication", f"{report['communication_score']}/10")
    col2.metric("Technical", f"{report['technical_score']}/10")
    col3.metric("Confidence", f"{report['confidence_score']}/10")
    col4.metric("Overall", f"{report['overall_score']}/10")

    st.plotly_chart(_radar_chart(
        report["communication_score"],
        report["technical_score"],
        report["confidence_score"]
    ), use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### ✅ Strengths")
        strengths = report.get("strengths", "[]")
        try:
            import ast
            items = ast.literal_eval(strengths)
            for s in items:
                st.markdown(f"- {s}")
        except Exception:
            st.write(strengths)

    with col_r:
        st.markdown("#### ⚠️ Areas to Improve")
        weaknesses = report.get("weaknesses", "[]")
        try:
            import ast
            items = ast.literal_eval(weaknesses)
            for w in items:
                st.markdown(f"- {w}")
        except Exception:
            st.write(weaknesses)

    st.markdown("#### 📋 Detailed Feedback")
    st.info(report.get("detailed_feedback", "No feedback available."))

    rec = report.get("recommendation", "consider")
    rec_map = {
        "strong_hire": ("🟢 Strong Hire", "success"),
        "hire": ("🟡 Hire", "success"),
        "consider": ("🟠 Consider", "warning"),
        "reject": ("🔴 Reject", "error"),
    }
    label, kind = rec_map.get(rec, ("Unknown", "info"))
    getattr(st, kind)(f"**Hiring Recommendation:** {label}")


def render_interview_analysis_recruiter():
    """Recruiter view of all completed interviews."""
    st.subheader("🧠 Interview Analysis Dashboard")

    jobs = db.get_all_jobs()
    if not jobs:
        st.info("No jobs found.")
        return

    job_options = {f"[{j['id']}] {j['title']}": j["id"] for j in jobs}
    sel = st.selectbox("Filter by Job", ["All Jobs"] + list(job_options.keys()))

    if sel == "All Jobs":
        query = """
            SELECT i.id as interview_id, i.status, i.completed_at,
                   c.full_name, j.title as job_title,
                   ir.overall_score, ir.recommendation,
                   ir.communication_score, ir.technical_score, ir.confidence_score
            FROM interviews i
            JOIN applications a ON i.application_id = a.id
            JOIN candidates c ON a.candidate_id = c.id
            JOIN jobs j ON a.job_id = j.id
            LEFT JOIN interview_reports ir ON ir.interview_id = i.id
            ORDER BY ir.overall_score DESC
        """
        rows = db.fetchall(query)
    else:
        job_id = job_options[sel]
        query = """
            SELECT i.id as interview_id, i.status, i.completed_at,
                   c.full_name, j.title as job_title,
                   ir.overall_score, ir.recommendation,
                   ir.communication_score, ir.technical_score, ir.confidence_score
            FROM interviews i
            JOIN applications a ON i.application_id = a.id
            JOIN candidates c ON a.candidate_id = c.id
            JOIN jobs j ON a.job_id = j.id
            LEFT JOIN interview_reports ir ON ir.interview_id = i.id
            WHERE j.id = ?
            ORDER BY ir.overall_score DESC
        """
        rows = db.fetchall(query, (job_id,))

    if not rows:
        st.info("No completed interviews found.")
        return

    for row in rows:
        with st.expander(f"👤 {row['full_name']} — {row['job_title']} | Score: {row.get('overall_score') or 'Pending'}"):
            if row.get("overall_score"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Communication", f"{row['communication_score']}/10")
                col2.metric("Technical", f"{row['technical_score']}/10")
                col3.metric("Confidence", f"{row['confidence_score']}/10")
                col4.metric("Overall", f"{row['overall_score']}/10")

                st.plotly_chart(_radar_chart(
                    row["communication_score"],
                    row["technical_score"],
                    row["confidence_score"]
                ), use_container_width=True)

                rec = row.get("recommendation", "consider")
                rec_labels = {"strong_hire": "🟢 Strong Hire", "hire": "🟡 Hire",
                              "consider": "🟠 Consider", "reject": "🔴 Reject"}
                st.markdown(f"**Recommendation:** {rec_labels.get(rec, rec)}")

                report = db.get_interview_report(row["interview_id"])
                if report:
                    st.info(report.get("detailed_feedback", ""))
            else:
                st.warning("Interview uploaded but not yet analyzed.")
