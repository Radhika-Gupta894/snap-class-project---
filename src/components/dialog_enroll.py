import streamlit as st
from src.database.db import enroll_student_to_subject, normalize_subject
from src.database.config import supabase

import time


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write('Enter the subject code provided by your teacher to enroll')
    join_code = st.text_input('Subject Code', placeholder='Eg. CS101')

    if st.button('Enroll now', type="primary", width='stretch'):
        if join_code:
            code_clean = join_code.strip()
            res = None
            for col in ['code', 'join_code', 'subject_code']:
                try:
                    q_res = supabase.table('subjects').select('*').eq(col, code_clean).execute()
                    if q_res.data:
                        res = q_res
                        break
                except Exception:
                    pass

            if res and res.data:
                subject = normalize_subject(res.data[0])
                student_id = st.session_state.student_data['student_id']
                sub_id_val = subject['subject_id']

                check = supabase.table('subject_students').select('*').eq('subject_id', sub_id_val).eq('student_id', student_id).execute()
                if check.data:
                    st.warning('You are already enrolled in this subject')
                else:
                    enroll_student_to_subject(student_id, sub_id_val)
                    st.success('Successfully enrolled!')
                    time.sleep(1)
                    st.rerun()
            else:
                st.error('Subject Code not found!')
        else:
            st.warning('Please enter a subject code')
