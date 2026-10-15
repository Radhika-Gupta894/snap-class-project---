import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

from src.components.dialog_auto_enroll import auto_enroll_dialog

def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendance faster using AI',
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
    )
    
    try:
        # Query parameter support (e.g. ?portal=teacher or ?portal=student)
        portal_param = st.query_params.get('portal') or st.query_params.get('role')
        if portal_param and st.session_state.get('login_type') is None:
            if portal_param in ['teacher', 'student']:
                st.session_state['login_type'] = portal_param

        if 'login_type' not in st.session_state:
            st.session_state['login_type'] = None

        match st.session_state['login_type']:
            case 'teacher':
                teacher_screen()

            case 'student':
                student_screen()
            
            case None:
                home_screen()

        join_code = st.query_params.get('join-code')
        if join_code:
            if st.session_state.login_type != 'student':
                st.session_state.login_type = 'student'
                st.rerun()
            if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
                auto_enroll_dialog(join_code)
                
    except Exception as e:
        err_msg = str(e)
        if "getaddrinfo failed" in err_msg or "ConnectError" in err_msg or "11001" in err_msg:
            configured_url = st.secrets.get("supabase_URL", "Unknown")
            st.error("### ⚠️ Database Connection Failure")
            st.warning(f"""
            We were unable to connect to the Supabase database URL specified in your secrets config:
            `{configured_url}`
            
            **Possible Causes:**
            1. **Expired or Paused Database**: Supabase automatically pauses or deletes free-tier databases after a period of inactivity.
            2. **DNS Resolution Failure**: The domain is no longer registered.
            3. **Offline**: You may not be connected to the internet.
            
            **How to fix this:**
            * Open your [Supabase Dashboard](https://supabase.com/dashboard) and retrieve your active **Project URL** and **anon public Key**.
            * Edit the `.streamlit/secrets.toml` file in the root of this project and replace the keys:
            ```toml
            supabase_URL = "https://your-new-project-id.supabase.co"
            supabase_API = "your-new-anon-public-key"
            ```
            """)
        elif "row-level security" in err_msg or "42501" in err_msg:
            st.error("### ⚠️ Supabase Row-Level Security (RLS) Blocking Operation")
            st.warning("""
            Your Supabase database has Row-Level Security (RLS) active, preventing read/write operations from the app.
            
            **Quick Fix:**
            Run the following in your **Supabase SQL Editor**:
            ```sql
            ALTER TABLE IF EXISTS teachers DISABLE ROW LEVEL SECURITY;
            ALTER TABLE IF EXISTS students DISABLE ROW LEVEL SECURITY;
            ALTER TABLE IF EXISTS subjects DISABLE ROW LEVEL SECURITY;
            ALTER TABLE IF EXISTS subject_students DISABLE ROW LEVEL SECURITY;
            ALTER TABLE IF EXISTS attendance DISABLE ROW LEVEL SECURITY;
            ALTER TABLE IF EXISTS attendance_logs DISABLE ROW LEVEL SECURITY;
            ```
            """)
        else:
            st.error("### ⚠️ An unexpected error occurred")
            st.exception(e)

if __name__ == "__main__":
    main()