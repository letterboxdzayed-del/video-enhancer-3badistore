import os
import subprocess
import tempfile
import pyotp
import streamlit as st

# ==========================================
# 1. إعدادات الصفحة والأمان
# ==========================================
st.set_page_config(
    page_title="3badiJO CC Engine",
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
    st.title("🔒 3badiJO CC Engine")
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

st.title("🎬 3badiJO Cinematic CC Engine")
st.caption("مُعالج الجودة السينمائية السريع (Sharpen + Contrast + Color Boost)")

if st.session_state.is_admin:
    current_otp = totp.now()
    st.info(f"🔑 رمز المشترك الحالي: **{current_otp}**")


# ==========================================
# 3. دالة معالجة الفيديو بالـ FFmpeg (سريعة جداً)
# ==========================================
def apply_cinematic_cc(input_path, output_path, preset_style):
    """
    معالجة الفيديو مباشرة باستخدام FFmpeg للسرعة العالية وبدون استهلاك رصيد.
    """
    # فلاتر معالجة الصورة بناءً على النمط المختاري
    if preset_style == "سينمائي حاد (Sharpen + High Contrast)":
        # زيادة حدة التفاصيل (unsharp)، إبراز التباين والتشبع (eq)
        vf_filter = "unsharp=5:5:1.5:5:5:0.0,eq=contrast=1.18:brightness=0.01:saturation=1.25"
    elif preset_style == "ألوان مشبعة 4K (Vibrant)":
        vf_filter = "unsharp=3:3:1.0,eq=contrast=1.10:saturation=1.40:gamma=1.05"
    else:  # توضيح ناعم (Soft Clarity)
        vf_filter = "unsharp=3:3:0.8,eq=contrast=1.08:saturation=1.15"

    # أمر FFmpeg لمعالجة الفيديو بأعلى جودة وبأسرع وقت (ultrafast preset)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vf",
        vf_filter,
        "-c:v",
        "libx264",
        "-crf",
        "17",  # جودة مخرجات عالية جداً (Bitrate ممتاز)
        "-preset",
        "ultrafast",  # معالجة فائقة السرعة
        "-c:a",
        "copy",  # الحفاظ على الصوت كما هو
        output_path,
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0


# ==========================================
# 4. الواجهة الرئيسية للرفع والتعديل
# ==========================================
uploaded_file = st.file_uploader(
    "ارفع مقطع الفيديو للتعديل السينمائي:", type=["mp4", "mov"]
)

if uploaded_file is not None:
    st.video(uploaded_file)

    # اختيار نمط الفلتر
    preset = st.selectbox(
        "اختر نمط الفلتر السينمائي (CC Preset):",
        [
            "سينمائي حاد (Sharpen + High Contrast)",
            "ألوان مشبعة 4K (Vibrant)",
            "توضيح ناعم (Soft Clarity)",
        ],
    )

    if st.button("معالجة الفيديو فوراً ⚡"):
        with st.spinner("جاري تطبيق فلاتر الـ CC والحدة خلال ثوانٍ..."):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as in_file:
                in_file.write(uploaded_file.read())
                in_path = in_file.name

            out_path = in_path.replace(".mp4", "_processed.mp4")

            success = apply_cinematic_cc(in_path, out_path, preset)

            if success and os.path.exists(out_path):
                st.success("تمت المعالجة بنجاح وبسرعة فائقة! 🔥")
                st.video(out_path)

                # زر تنزيل الفيديو الناتج
                with open(out_path, "rb") as file:
                    st.download_button(
                        label="📥 تحميل الفيديو المعدل",
                        data=file,
                        file_name="3badiJO_Enhanced.mp4",
                        mime="video/mp4",
                    )
            else:
                st.error("حدث خطأ أثناء معالجة الفيديو بواسطة FFmpeg.")
