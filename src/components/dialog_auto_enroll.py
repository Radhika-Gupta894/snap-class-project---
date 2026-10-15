import streamlit as st
from src.database.db import enroll_student_to_subject, normalize_subject
from src.database.config import supabase

import time


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data['student_id']
    code_clean = subject_code.strip()

    res = None
    for col in ['code', 'join_code', 'subject_code']:
        try:
            q_res = supabase.table('subjects').select('*').eq(col, code_clean).execute()
            if q_res.data:
                res = q_res
                break
        except Exception:
            pass

    if not res or not res.data:
        st.error('Subject Code not found!')
        if st.button('Close'):
            st.query_params.clear()
            st.rerun()
        return

    subject = normalize_subject(res.data[0])
    sub_id_val = subject['subject_id']

    check = supabase.table('subject_students').select('*').eq('subject_id', sub_id_val).eq('student_id', student_id).execute()
    if check.data:
        st.info('You are already enrolled!')
        if st.button('Got it!'):
            st.query_params.clear()
            st.rerun()
        return
    st.markdown(f"Would you like to enroll in **{subject['name']}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('No thanks'):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button('Yes enroll now!', type='primary', width='stretch'):
            enroll_student_to_subject(student_id, sub_id_val)
            st.success('Joined successfully!')
            st.query_params.clear()
            time.sleep(2)
            st.rerun()