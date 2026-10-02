import gc
import json
import os
import re
import subprocess
import tempfile
import threading
import imageio_ffmpeg
import streamlit as st

# ==========================================
# 1. إعدادات الصفحة والأمان وقاعدة البيانات
# ==========================================
st.set_page_config(
    page_title="3badiJO Engine",
    page_icon="🎬",
    layout="centered",
)

ADMIN_PASSWORD = "zayed321abadi"
USERS_FILE = "users.json"


# دالة تحميل حسابات المشتركين
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # حسابات افتراضية في حال عدم وجود الملف
    return {"client1": "123456", "test_user": "3badi2026"}


# دالة حفظ حسابات المشتركين
def save_users(users_dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_dict, f, ensure_ascii=False, indent=4)


if "users_db" not in st.session_state:
    st.session_state.users_db = load_users()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_username" not in st.session_state:
    st.session_state.current_username = ""


# ==========================================
# 2. نظام تسجيل الدخول ولوحة التحكم
# ==========================================
def check_auth():
    st.title("🔒 3badiJO Engine")
    tab1, tab2 = st.tabs(["دخول المشتركين 👤", "لوحة المؤسس 👑"])

    with tab1:
        username_input = st.text_input("اسم المستخدم:", key="user_name_input")
        password_input = st.text_input(
            "كلمة المرور:", type="password", key="user_pass_input"
        )

        if st.button("دخول المشتركين", key="btn_user"):
            users = st.session_state.users_db
            if (
                username_input in users
                and users[username_input] == password_input
            ):
                st.session_state.authenticated = True
                st.session_state.is_admin = False
                st.session_state.current_username = username_input
                st.success(f"أهلاً بك يا {username_input}! 👋")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

    with tab2:
        admin_pass = st.text_input(
            "كلمة سر المؤسس:", type="password", key="admin_input"
        )
        if st.button("دخول كـ مؤسس", key="btn_admin"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.session_state.current_username = "المؤسس"
                st.rerun()
            else:
                st.error("كلمة السر غير صحيحة!")


if not st.session_state.authenticated:
    check_auth()
    st.stop()

# ==========================================
# 3. القائمة الجانبية وإدارة الحسابات
# ==========================================
st.sidebar.success(
    f"🟢 أهلاً بك: **{st.session_state.current_username}**"
    + (" (المؤسس)" if st.session_state.is_admin else "")
)

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.session_state.current_username = ""
    st.rerun()

st.title("🎬 3badiJO Engine")

# لوحة خاصة للمؤسس لإضافة وحذف الحسابات
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("👑 لوحة إدارة المشتركين")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ➕ إضافة مشترك جديد")
        new_username = st.text_input("اسم المستخدم الجديد:", key="new_u")
        new_password = st.text_input("كلمة المرور الجديدة:", key="new_p")

        if st.button("حفظ المشترك 💾"):
            if new_username and new_password:
                st.session_state.users_db[new_username] = new_password
                save_users(st.session_state.users_db)
                st.success(f"تمت إضافة المشترك `{new_username}` بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى إدخال اسم المستخدم وكلمة المرور.")

    with col2:
        st.markdown("### 📋 المشتركين الحاليين")
        users_list = st.session_state.users_db
        for u, p in list(users_list.items()):
            col_u, col_del = st.columns([3, 1])
            col_u.write(f"👤 **{u}** (كلمة السر: `{p}`)")
            if col_del.button("❌", key=f"del_{u}"):
                del st.session_state.users_db[u]
                save_users(st.session_state.users_db)
                st.success(f"تم حذف المشترك {u}")
                st.rerun()

    st.markdown("---")


@st.cache_resource
def get_global_lock():
    return threading.Lock()


server_lock = get_global_lock()


# ==========================================
# 4. دالة حساب طول الفيديو والمعالجة
# ==========================================
def get_video_duration(ffmpeg_exe, input_path):
    cmd = [ffmpeg_exe, "-i", input_path]
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    _, stderr = p.communicate()
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
    if match:
        hours, minutes, seconds = map(float, match.groups())
        return hours * 3600 + minutes * 60 + seconds
    return None


def enhance_video_quality(input_path, output_path, lighting_mode):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    if lighting_mode == "low_light":
        # إضاءة منخفضة: CAS 0.57 | Unsharp 1.41 | Contrast 1.19 | Brightness 0.10 | Saturation 1.20
        vf_filter = (
            "hqdn3d=2.0:2.0:3:3,"
            "cas=0.57,"
            "unsharp=5:5:1.41:5:5:0.0,"
            "eq=contrast=1.19:brightness=0.10:saturation=1.20,"
            "scale='min(1080,iw)':-2:flags=lanczos"
        )
    else:
        # إضاءة عالية: CAS 0.59 | Unsharp 1.42 | Contrast 1.23 | Brightness 0.09 | Saturation 1.20
        vf_filter = (
            "hqdn3d=2.0:2.0:3:3,"
            "cas=0.59,"
            "unsharp=5:5:1.42:5:5:0.0,"
            "eq=contrast=1.23:brightness=0.09:saturation=1.20,"
            "scale='min(1080,iw)':-2:flags=lanczos"
        )

    command = [
        ffmpeg_exe,
        "-y",
        "-i",
        input_path,
        "-vf",
        vf_filter,
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-preset",
        "veryfast",
        "-threads",
        "1",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "copy",
        output_path,
    ]

    total_duration = get_video_duration(ffmpeg_exe, input_path)

    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("⏳ جاري بدء معالجة الفيديو: 0%")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

    try:
        for line in process.stdout:
            match = time_pattern.search(line)
            if match and total_duration:
                h, m, s = map(float, match.groups())
                elapsed = h * 3600 + m * 60 + s
                progress = min(1.0, max(0.0, elapsed / total_duration))
                percent = int(progress * 100)
                progress_bar.progress(progress)
                status_text.text(f"⏳ جاري معالجة ورفع الجودة: {percent}%")

        process.wait()
        if process.returncode == 0:
            progress_bar.progress(1.0)
            status_text.text("✅ اكتملت المعالجة بنجاح 100%!")
            return True
        else:
            status_text.text("❌ حدث خطأ أثناء معالجة الفيديو.")
            return False
    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")
        return False


# ==========================================
# 5. الواجهة الرئيسية لرفع الفيديو
# ==========================================
st.markdown("### 💡 اختر نمط الفيديو الخاص بك، هل إضاءته عالية؟ أم منخفضة؟")
light_option = st.radio(
    "اختر نمط الإضاءة:",
    ["☀️ إضاءة عالية", "🌙 إضاءة منخفضة"],
    label_visibility="collapsed",
)

st.markdown("### 🎬 ارفع مقطع الفيديو:")
uploaded_file = st.file_uploader(
    "اختر مقطع فيديو:", type=["mp4", "mov"], label_visibility="collapsed"
)

if uploaded_file is not None:
    st.video(uploaded_file)

    mode_key = (
        "low_light" if "منخفضة" in light_option else "high_light"
    )

    if st.button("رفع جودة المقطع 🔥"):
        in_path = None
        out_path = None

        status_notice = st.info(
            "⏳ جاري تجهيز الطلب والتأكد من توفر السيرفر..."
        )

        with server_lock:
            status_notice.empty()
            try:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp4"
                ) as in_file:
                    in_file.write(uploaded_file.read())
                    in_path = in_file.name

                out_path = in_path.replace(".mp4", "_processed.mp4")

                success = enhance_video_quality(
                    in_path, out_path, mode_key
                )

                if success and os.path.exists(out_path):
                    st.video(out_path)

                    with open(out_path, "rb") as file:
                        st.download_button(
                            label="📥 تحميل المقطع",
                            data=file,
                            file_name="3badiJO_Enhanced.mp4",
                            mime="video/mp4",
                        )
                else:
                    st.error("لم تتم معالجة الفيديو بنجاح.")
            finally:
                if in_path and os.path.exists(in_path):
                    os.remove(in_path)
                if out_path and os.path.exists(out_path):
                    os.remove(out_path)
                gc.collect()
