import os
import tempfile
import pyotp
import replicate
import streamlit as st

# ==========================================
# 1. إعدادات الصفحة والأمان
# ==========================================
st.set_page_config(
    page_title="3badiJO AI Engine",
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
    st.title("🔒 3badiJO AI Engine")
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

st.title("🎬 3badiJO Replicate Video AI")

if st.session_state.is_admin:
    main_tab1, main_tab2 = st.tabs(["🔑 رمز المشترك", "🎬 معالجة الفيديو"])
    with main_tab1:
        current_otp = totp.now()
        st.success(f"🔑 الرمز الحالي:\n# **{current_otp}**")
    with main_tab2:
        st.write("رفع جودة الفيديوهات عبر Replicate GPU API")
else:
    st.write("رفع جودة الفيديوهات عبر Replicate GPU API")


# ==========================================
# 3. دالة المعالجة عبر Replicate للفيديو
# ==========================================
def upscale_video_with_replicate(video_path):
    try:
        with open(video_path, "rb") as file:
            # استخدام اسم الموديل المباشر العام بدون version مفردة لتفادي الأخطاء
            output = replicate.run(
                "lucataco/real-esrgan-video",
                input={
                    "video": file,
                    "upscale": 2,
                },
            )
        return output
    except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال بـ Replicate: {e}")
        return None


# ==========================================
# 4. الواجهة والرفع (فيديو فقط)
# ==========================================
uploaded_file = st.file_uploader(
    "ارفع مقطع فيديو لمعالجته بالـ AI:",
    type=["mp4", "mov"],
)

if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    st.video(uploaded_file)

    if st.button("رفع جودة الفيديو بالـ AI 🔥"):
        with st.spinner("جاري رفع الفيديو ومعالجته عبر كرت الشاشة السريع..."):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{file_ext}"
            ) as tmp_file:
                tmp_file.write(uploaded_file.read())
                result_url = upscale_video_with_replicate(tmp_file.name)

            if result_url:
                st.success("تمت معالجة الفيديو بنجاح!")
                st.video(result_url)
