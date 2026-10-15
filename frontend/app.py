import os
import shutil
import urllib.request
from flask import Flask, render_template

app = Flask(__name__)

# Configurable Streamlit URL for deployment
STREAMLIT_URL = os.environ.get("STREAMLIT_URL", "http://localhost:8501")

def setup_demo_images():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "static", "img")
    demo_dir = os.path.join(img_dir, "demo")
    os.makedirs(demo_dir, exist_ok=True)

    # 1. Download official logo if not present
    logo_path = os.path.join(img_dir, "logo.png")
    app_logo_path = os.path.join(img_dir, "app_logo.png")
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    if not os.path.exists(logo_path) or os.path.getsize(logo_path) == 0:
        try:
            req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp, open(logo_path, 'wb') as f:
                f.write(resp.read())
        except Exception:
            pass

    if os.path.exists(logo_path) and (not os.path.exists(app_logo_path) or os.path.getsize(app_logo_path) == 0):
        try:
            shutil.copyfile(logo_path, app_logo_path)
        except Exception:
            pass

    # 2. Map captured real screenshots to the expected landing page filenames
    brain_dir = r"C:\Users\shali\.gemini\antigravity-ide\brain\ff74099f-9b84-46b6-a9c3-e941e509bd74"
    screen_mappings = {
        "snap-landing.png": "screen_home_1792086949837.png",
        "snap-teacher-flow-1-login.png": "screen_teacher_login_1792086984286.png",
        "snap-teacher-flow-2-dashboard.png": "screen_teacher_dash_1792087016750.png",
        "snap-teacher-flow-3-create-course.png": "screen_manage_subjects_1792087033599.png",
        "snap-teacher-flow-5.2-photo-attendance.png": "screen_teacher_dash_1792087016750.png",
        "snap-teacher-flow-5.1-voice-attendance.png": "screen_teacher_dash_1792087016750.png",
        "snap-teacher-flow-5-see-stored-records.png": "screen_attendance_records_1792087048193.png",
    }

    fallback_source = os.path.join(brain_dir, "screen_home_1792086949837.png")
    for target_name, src_file in screen_mappings.items():
        dest = os.path.join(demo_dir, target_name)
        src_path = os.path.join(brain_dir, src_file)
        if not os.path.exists(dest) or os.path.getsize(dest) == 0:
            actual_src = src_path if os.path.exists(src_path) else fallback_source
            if os.path.exists(actual_src):
                try:
                    shutil.copyfile(actual_src, dest)
                except Exception:
                    pass

# Ensure demo assets are populated on startup
setup_demo_images()

@app.route('/')
def home():
    setup_demo_images()
    return render_template('index.html', streamlit_url=STREAMLIT_URL)

if __name__ == '__main__':
    app.run(debug=True, port=5002)