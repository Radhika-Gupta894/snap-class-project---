# import streamlit as st
from src.database.config import supabase
import bcrypt
from datetime import datetime

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_teacher_exists(username):
    # check for unique username, returns false when username is already taken
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0

def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            if 'teacher_id' not in teacher:
                teacher['teacher_id'] = teacher.get('username')
            return teacher
        return None

def get_all_students():
    response = supabase.table('students').select("*").execute()
    return response.data

_STUDENTS_COLS_CACHE = None

def get_existing_student_columns(refresh=False):
    global _STUDENTS_COLS_CACHE
    if _STUDENTS_COLS_CACHE is not None and not refresh:
        return _STUDENTS_COLS_CACHE

    test_cols = [
        'student_id', 'id', 'name',
        'face_embeddings', 'face_embedding',
        'voice_embeddings', 'voice_embedding',
        'created_at'
    ]
    found = set()
    for col in test_cols:
        try:
            supabase.table('students').select(col).limit(1).execute()
            found.add(col)
        except Exception:
            pass

    if found:
        _STUDENTS_COLS_CACHE = found
    return found

def create_student(new_name, face_embedding=None, voice_embedding=None, student_id=None):
    cols = get_existing_student_columns(refresh=True)

    # Detect face embedding column name in Supabase
    face_col = None
    if 'face_embeddings' in cols:
        face_col = 'face_embeddings'
    elif 'face_embedding' in cols:
        face_col = 'face_embedding'

    # Detect voice embedding column name in Supabase
    voice_col = None
    if 'voice_embeddings' in cols:
        voice_col = 'voice_embeddings'
    elif 'voice_embedding' in cols:
        voice_col = 'voice_embedding'

    if not face_col:
        raise Exception(
            "MISSING_EMBEDDING_COLUMN: The 'students' table in Supabase does not have 'face_embeddings' or 'face_embedding'. "
            "Please run: ALTER TABLE students ADD COLUMN IF NOT EXISTS face_embeddings JSONB; "
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS voice_embeddings JSONB; "
            "NOTIFY pgrst, 'reload schema';"
        )

    data = {'name': new_name}
    if face_col and face_embedding is not None:
        data[face_col] = face_embedding
    if voice_col and voice_embedding is not None:
        data[voice_col] = voice_embedding

    id_col = 'student_id' if 'student_id' in cols else ('id' if 'id' in cols else None)
    if id_col and student_id is not None:
        data[id_col] = student_id

    try:
        response = supabase.table('students').insert(data).execute()
        return response.data
    except Exception as e:
        err = str(e)
        if id_col and ("not-null" in err or "violates" in err):
            import time
            data[id_col] = str(int(time.time()) % 1000000)
            response = supabase.table('students').insert(data).execute()
            return response.data
        raise e

def normalize_subject(s):
    if not isinstance(s, dict):
        return s
    sid = s.get('subject_id') or s.get('code') or s.get('id')
    scode = s.get('subject_code') or s.get('code') or s.get('join_code') or sid
    s['subject_id'] = sid
    s['subject_code'] = scode
    return s

def get_existing_subject_columns():
    test_cols = ['code', 'subject_code', 'subject_id', 'id', 'name', 'section', 'teacher_username', 'teacher_id', 'join_code', 'created_at']
    found = set()
    for col in test_cols:
        try:
            supabase.table('subjects').select(col).limit(1).execute()
            found.add(col)
        except Exception:
            pass
    return found

def create_subject(subject_code, name, section, teacher_id):
    cols = get_existing_subject_columns()
    data = {"name": name, "section": section}
    if 'code' in cols:
        data['code'] = subject_code
    if 'subject_code' in cols:
        data['subject_code'] = subject_code
    if 'join_code' in cols:
        data['join_code'] = subject_code

    if 'teacher_username' in cols:
        data['teacher_username'] = teacher_id
    elif 'teacher_id' in cols:
        data['teacher_id'] = teacher_id

    response = supabase.table("subjects").insert(data).execute()
    return response.data

_ATTENDANCE_TABLE_NAME = None

def get_attendance_table_name():
    global _ATTENDANCE_TABLE_NAME
    if _ATTENDANCE_TABLE_NAME:
        return _ATTENDANCE_TABLE_NAME
    try:
        supabase.table('attendance').select('count', count='exact').limit(0).execute()
        _ATTENDANCE_TABLE_NAME = 'attendance'
        return 'attendance'
    except Exception:
        _ATTENDANCE_TABLE_NAME = 'attendance_logs'
        return 'attendance_logs'

def get_existing_attendance_columns(table_name):
    test_cols = ['id', 'subject_id', 'student_id', 'is_present', 'date', 'timestamp', 'created_at']
    found = set()
    for col in test_cols:
        try:
            supabase.table(table_name).select(col).limit(1).execute()
            found.add(col)
        except Exception:
            pass
    return found

def get_teacher_subjects(teacher_id):
    table_name = get_attendance_table_name()
    cols = get_existing_subject_columns()
    teacher_cols = ['teacher_username', 'teacher_id'] if 'teacher_username' in cols else ['teacher_id', 'teacher_username']

    subjects = []
    for t_col in teacher_cols:
        try:
            query = f"*, subject_students(count), {table_name}(*)"
            response = supabase.table('subjects').select(query).eq(t_col, teacher_id).execute()
            if response.data:
                subjects = response.data
                break
        except Exception:
            try:
                response = supabase.table('subjects').select("*, subject_students(count)").eq(t_col, teacher_id).execute()
                if response.data:
                    subjects = response.data
                    break
            except Exception:
                pass

    for sub in subjects:
        normalize_subject(sub)
        # Get count of enrolled students
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0

        # Calculate number of unique classes taken based on attendance log timestamps
        attendance = sub.get(table_name) or sub.get('attendance') or sub.get('attendance_logs') or []
        if attendance:
            unique_session = len(set(
                log.get('timestamp') or str(log.get('date')) or str(log.get('created_at'))
                for log in attendance if (log.get('timestamp') or log.get('date') or log.get('created_at'))
            ))
        else:
            unique_session = 0
        sub['total_classes'] = unique_session

        # Clean up temporary database relational keys
        sub.pop('subject_students', None)
        sub.pop(table_name, None)
        sub.pop('attendance_logs', None)
        sub.pop('attendance', None)

    return subjects

def enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response = supabase.table('subject_students').insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id, subject_id):
    response = supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return response.data

def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    data = response.data or []
    for item in data:
        if isinstance(item.get('subjects'), dict):
            normalize_subject(item['subjects'])
    return data

def get_student_attendance(student_id):
    table_name = get_attendance_table_name()
    try:
        response = supabase.table(table_name).select('*, subjects(*)').eq('student_id', student_id).execute()
        return response.data
    except Exception:
        alt_table = 'attendance_logs' if table_name == 'attendance' else 'attendance'
        try:
            response = supabase.table(alt_table).select('*, subjects(*)').eq('student_id', student_id).execute()
            return response.data
        except Exception:
            return []

def create_attendance(logs):
    table_name = get_attendance_table_name()
    cols = get_existing_attendance_columns(table_name)
    sanitized_logs = []
    for log in logs:
        item = dict(log)
        if 'date' in cols and 'date' not in item:
            ts = item.get('timestamp') or datetime.now().isoformat()
            item['date'] = ts[:10]
        if 'timestamp' not in cols and 'timestamp' in item and 'date' in cols:
            item.pop('timestamp', None)
        sanitized_logs.append(item)

    try:
        response = supabase.table(table_name).insert(sanitized_logs).execute()
        return response.data
    except Exception:
        alt_table = 'attendance_logs' if table_name == 'attendance' else 'attendance'
        response = supabase.table(alt_table).insert(sanitized_logs).execute()
        return response.data

def get_attendance_for_teacher(teacher_id):
    table_name = get_attendance_table_name()
    try:
        response = supabase.table(table_name).select('*, subjects!inner(*)').eq('subjects.teacher_id', teacher_id).execute()
        return response.data
    except Exception:
        alt_table = 'attendance_logs' if table_name == 'attendance' else 'attendance'
        try:
            response = supabase.table(alt_table).select('*, subjects!inner(*)').eq('subjects.teacher_id', teacher_id).execute()
            return response.data
        except Exception:
            return []

def get_all_teachers():
    try:
        response = supabase.table("teachers").select("username, name").execute()
        return response.data or []
    except Exception:
        return []

def get_or_create_demo_teacher():
    try:
        teachers = supabase.table("teachers").select("*").limit(1).execute()
        if teachers.data:
            t = dict(teachers.data[0])
            if 'teacher_id' not in t:
                t['teacher_id'] = t.get('username')
            return t
        
        demo_t = {
            "username": "demo_teacher",
            "name": "Prof. Demo",
            "password": hash_pass("123456")
        }
        supabase.table("teachers").insert(demo_t).execute()
        demo_t['teacher_id'] = "demo_teacher"
        return demo_t
    except Exception:
        return {"username": "demo_teacher", "teacher_id": "demo_teacher", "name": "Prof. Demo"}

def get_or_create_demo_student():
    try:
        students = supabase.table("students").select("*").limit(1).execute()
        if students.data:
            s = dict(students.data[0])
            if 'student_id' not in s:
                s['student_id'] = s.get('id')
            return s
        
        demo_s = {
            "student_id": "STU_DEMO_01",
            "name": "Demo Student",
        }
        supabase.table("students").insert(demo_s).execute()
        return demo_s
    except Exception:
        return {"student_id": "STU_DEMO_01", "name": "Demo Student"}
