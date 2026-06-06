"""
modules/onboarding.py — Onboarding workflow: offer letters, checklist, joining status
"""
import streamlit as st
import json
from database import db
from utils.file_handler import save_onboarding_doc


def render_onboarding_recruiter():
    st.subheader("🎉 Onboarding Management")

    hired = db.fetchall("""
        SELECT c.id as candidate_id, c.full_name, u.email, a.id as app_id, j.title as job_title
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON c.user_id = u.id
        WHERE a.status IN ('offered', 'hired')
        ORDER BY a.updated_at DESC
    """)

    if not hired:
        st.info("No candidates in the offered/hired stage yet.")
        return

    for h in hired:
        cid = h["candidate_id"]
        db.create_onboarding(cid)
        onboarding = db.get_onboarding(cid)

        with st.expander(f"👤 {h['full_name']} — {h['job_title']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                offer_status = st.selectbox(
                    "Offer Status", ["pending", "sent", "accepted", "declined"],
                    index=["pending", "sent", "accepted", "declined"].index(onboarding["offer_status"]),
                    key=f"offer_{cid}"
                )
            with col2:
                joining_status = st.selectbox(
                    "Joining Status", ["pending", "confirmed", "joined", "no_show"],
                    index=["pending", "confirmed", "joined", "no_show"].index(onboarding["joining_status"]),
                    key=f"join_{cid}"
                )
            with col3:
                joining_date = st.date_input("Joining Date", key=f"date_{cid}")

            if st.button("💾 Save Status", key=f"save_{cid}"):
                db.update_onboarding(
                    cid,
                    offer_status=offer_status,
                    joining_status=joining_status,
                    joining_date=str(joining_date),
                )
                st.success("Saved!")
                st.rerun()

            # Document checklist
            st.markdown("**📁 Document Checklist**")
            try:
                checklist = json.loads(onboarding.get("doc_checklist") or "{}")
            except Exception:
                checklist = {}

            updated = False
            cols = st.columns(2)
            for i, (doc, checked) in enumerate(checklist.items()):
                with cols[i % 2]:
                    new_val = st.checkbox(doc, value=checked, key=f"doc_{cid}_{doc}")
                    if new_val != checked:
                        checklist[doc] = new_val
                        updated = True

            if updated:
                db.update_onboarding(cid, doc_checklist=json.dumps(checklist))
                st.rerun()

            completed = sum(checklist.values())
            total = len(checklist)
            st.progress(completed / total if total > 0 else 0,
                        text=f"Documents: {completed}/{total} submitted")


def render_onboarding_candidate(candidate_id: int):
    st.subheader("🎉 Your Onboarding")
    onboarding = db.get_onboarding(candidate_id)

    if not onboarding:
        st.info("Onboarding not started. Contact your recruiter.")
        return

    col1, col2 = st.columns(2)
    col1.metric("Offer Status", onboarding["offer_status"].title())
    col2.metric("Joining Status", onboarding["joining_status"].title())

    if onboarding.get("joining_date"):
        st.info(f"📅 Joining Date: **{onboarding['joining_date']}**")

    st.markdown("### 📁 Document Checklist")
    try:
        checklist = json.loads(onboarding.get("doc_checklist") or "{}")
    except Exception:
        checklist = {}

    completed = sum(checklist.values())
    total = len(checklist)
    st.progress(completed / total if total > 0 else 0,
                text=f"{completed}/{total} documents submitted")

    for doc, status in checklist.items():
        icon = "✅" if status else "⏳"
        st.markdown(f"{icon} {doc}")

    st.markdown("### 📤 Upload Documents")
    upload = st.file_uploader("Upload onboarding document", type=["pdf", "jpg", "png", "docx"])
    if upload:
        if st.button("📤 Submit Document"):
            file_bytes = upload.read()
            save_onboarding_doc(file_bytes, upload.name, candidate_id)
            st.success(f"'{upload.name}' uploaded successfully!")
