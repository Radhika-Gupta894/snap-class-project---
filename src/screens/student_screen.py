import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject, get_or_create_demo_student
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data.get('student_id') or student_data.get('id')
    student_data['student_id'] = student_id
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data 
            st.rerun()


    st.space()

    c1, c2 =st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()


    st.divider()


    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node.get('subjects')
        if not sub:
            continue
        sid = sub.get('subject_id') or sub.get('code') or sub.get('id')
        stats = stats_map.get(sid, {"total": 0, "attended": 0})
        
        def make_unenroll_callback(subject_id, subject_name):
            def unenroll_button():
                if st.button("Unenroll from this course", type='tertiary', width='stretch', icon=':material/delete_forever:', key=f"unenroll_{subject_id}"):
                    unenroll_student_to_subject(student_id, subject_id)
                    st.toast(f'Unenrolled from {subject_name} successfully!')
                    st.rerun()
            return unenroll_button

        with cols[i % 2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=make_unenroll_callback(sid, sub['name'])
            )
    footer_dashboard()


def student_screen():


    style_background_dashboard()
    style_base_layout()


    if "student_data" in st.session_state:
        if 'student_id' not in st.session_state.student_data:
            st.session_state.student_data['student_id'] = st.session_state.student_data.get('id')
        student_dashboard()
        return
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    # Direct bypass and student picker at top
    st.write("")
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if st.button('⚡ Open Student Dashboard Directly (Demo / Bypass)', type='secondary', use_container_width=True):
            demo_s = get_or_create_demo_student()
            st.session_state.is_logged_in = True
            st.session_state.user_role = 'student'
            st.session_state.student_data = demo_s
            st.rerun()
    with c_b2:
        try:
            existing_students = get_all_students()
            if existing_students:
                std_options = {f"{s.get('name', 'Student')} (ID: {s.get('student_id') or s.get('id')})": s for s in existing_students}
                selected_std_label = st.selectbox("Or choose existing registered student:", list(std_options.keys()), label_visibility="collapsed")
                if st.button("Login with Selected Profile", type="primary", use_container_width=True):
                    chosen = std_options[selected_std_label]
                    if 'student_id' not in chosen:
                        chosen['student_id'] = chosen.get('id')
                    st.session_state.is_logged_in = True
                    st.session_state.user_role = 'student'
                    st.session_state.student_data = chosen
                    st.rerun()
        except Exception:
            pass

    st.divider()

    tab_face_login, tab_register = st.tabs(["📷 FaceID Login", "➕ Register New Student"])

    with tab_face_login:
        st.header('Login using FaceID', text_alignment='center')
        st.space()
        photo_source = st.camera_input("Position your face in the center", key="login_cam")

        if photo_source:
            img = np.array(Image.open(photo_source))

            with st.spinner('AI is scanning..'):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning('Face not found!')
                elif num_faces > 1:
                    st.warning('Multiple faces found')
                else:
                    if detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next((s for s in all_students if str(s.get('student_id') or s.get('id'))==str(student_id)), None)

                        if student:
                            if 'student_id' not in student:
                                student['student_id'] = student.get('id')
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = student
                            st.toast(f'Welcome Back {student.get("name", "Student")}')
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.info('Face not recognized! Switch to the "Register New Student" tab to create your profile.')

    with tab_register:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi', key="reg_name_input")

            st.subheader('Face Photo for AI Recognition')
            reg_photo = st.camera_input("Capture Face Photo", key="reg_camera")
            if not reg_photo:
                reg_photo = st.file_uploader("Or Upload Face Photo (JPG/PNG)", type=["jpg", "jpeg", "png"], key="reg_upload")

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll for voice attendance")

            audio_data = None
            try:
                audio_data = st.audio_input('Record a short phrase like "I am present".', key="reg_audio")
            except Exception:
                st.error('Audio Data failed!')

            if st.button('Create Account', type='primary', key='btn_create_std_account'):
                if not new_name:
                    st.warning('Please enter your name!')
                elif not reg_photo:
                    st.warning('Please capture or upload a face photo!')
                else:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(reg_photo))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = None
                            try:
                                response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)
                            except Exception as e:
                                err_str = str(e)
                                if "MISSING_EMBEDDING_COLUMN" in err_str:
                                    st.error("### ⚠️ Supabase Schema Setup Required")
                                    st.warning("""
                                    Your Supabase `students` table does not have the embedding columns yet.
                                    
                                    **To fix this:**
                                    1. Open your [Supabase Dashboard](https://supabase.com/dashboard) -> Select your project.
                                    2. Go to **SQL Editor** -> **New Query**.
                                    3. Paste the following and click **Run**:
                                    ```sql
                                    ALTER TABLE students ADD COLUMN IF NOT EXISTS face_embeddings JSONB;
                                    ALTER TABLE students ADD COLUMN IF NOT EXISTS voice_embeddings JSONB;
                                    NOTIFY pgrst, 'reload schema';
                                    ```
                                    4. Then click **Create Account** again!
                                    """)
                                elif "row-level security" in err_str or "42501" in err_str:
                                    st.error("### ⚠️ Row-Level Security (RLS) Enabled on Supabase")
                                    st.warning("""
                                    Your Supabase database has Row-Level Security (RLS) turned on, which blocks writes from the app.
                                    
                                    **To fix this:**
                                    1. Open your [Supabase Dashboard](https://supabase.com/dashboard) -> Select your project.
                                    2. Go to **SQL Editor** -> **New Query**.
                                    3. Paste the following and click **Run**:
                                    ```sql
                                    ALTER TABLE students DISABLE ROW LEVEL SECURITY;
                                    ALTER TABLE teachers DISABLE ROW LEVEL SECURITY;
                                    ALTER TABLE subjects DISABLE ROW LEVEL SECURITY;
                                    ALTER TABLE subject_students DISABLE ROW LEVEL SECURITY;
                                    ALTER TABLE attendance_logs DISABLE ROW LEVEL SECURITY;
                                    ```
                                    4. Then click **Create Account** again!
                                    """)
                                else:
                                    st.error(f"Error creating profile: {e}")

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile Created! Hi {new_name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Could not extract facial features from the image. Please ensure your face is well-lit and facing the camera.')

    footer_dashboard()