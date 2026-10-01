import os
import subprocess
import tempfile
import imageio_ffmpeg
import pyotp
import streamlit as st

# ==========================================
# 1. إعدادات الصفحة والأمان
# ==========================================
st.set_page_config(
    page_title="3badiJO Engine",
    page_icon="🎬",
    layout="centered",
)

ADMIN_PASSWORD = "zayed321abadi"
USER_SECRET = "JBSWY3DPEHPK3PXP"
totp = pyotp.TOTP(USER_SECRET, interval=300)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


def check_auth():
    st.title("🔒 3badiJO Engine")
    tab1, tab2 = st.tabs(["دخول المشتركين 👤", "لوحة المؤسس 👑"])

    with tab1:
        user_code = st.text_input(
            "رمز الوصول:", type="password", key="user_input"
        )
        if st.button("دخول", key="btn_user"):
            if totp.verify(user_code):
                st.session_state.authenticated = True
                st.session_state.is_admin = False
                st.rerun()
            else:
                st.error("الرمز غير صحيح!")

    with tab2:
        admin_pass = st.text_input(
            "كلمة سر المؤسس:", type="password", key="admin_input"
        )
        if st.button("دخول كـ مؤسس", key="btn_admin"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("كلمة السر غير صحيحة!")


if not st.session_state.authenticated:
    check_auth()
    st.stop()

# ==========================================
# 2. القائمة الجانبية
# ==========================================
st.sidebar.success(
    "🟢 أهلاً بك"
    + (" (المؤسس)" if st.session_state.is_admin else " (مشترك)")
)
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.rerun()

st.title("🎬 3badiJO Engine")
st.write("رفع جودة المقطع")

if st.session_state.is_admin:
    current_otp = totp.now()
    st.info(f"🔑 رمز المشترك الحالي: **{current_otp}**")


# ==========================================
# 3. دالة معالجة الفيديو الديناميكية
# ==========================================
def enhance_video_quality(input_path, output_path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # normalize: تباين ديناميكي تلقائي يحلل الفيديو + زيادة تشبع إضافية + حدة تفاصيل
    vf_filter = "normalize=independence=0:strength=0.75,unsharp=5:5:1.2:5:5:0.0,eq=saturation=1.38"

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
        "16",
        "-preset",
        "ultrafast",
        "-c:a",
        "copy",
        output_path,
    ]

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0


# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
uploaded_file = st.file_uploader("ارفع مقطع الفيديو:", type=["mp4", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("رفع جودة المقطع 🔥"):
        with st.spinner("جاري معالجة الفيديو ورفع الجودة..."):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as in_file:
                in_file.write(uploaded_file.read())
                in_path = in_file.name

            out_path = in_path.replace(".mp4", "_processed.mp4")

            success = enhance_video_quality(in_path, out_path)

            if success and os.path.exists(out_path):
                st.success("تمت المعالجة بنجاح!")
                st.video(out_path)

                with open(out_path, "rb") as file:
                    st.download_button(
                        label="📥 تحميل المقطع",
                        data=file,
                        file_name="3badiJO_Enhanced.mp4",
                        mime="video/mp4",
                    )
            else:
                st.error("حدث خطأ أثناء معالجة الفيديو.")
