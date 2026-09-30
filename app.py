import os
import subprocess
import tempfile
import cv2
import numpy as np
import pyotp
import replicate
import streamlit as st
from PIL import Image

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

st.title("⚡ 3badiJO Replicate AI Upscaler")

if st.session_state.is_admin:
    main_tab1, main_tab2 = st.tabs(["🔑 رمز المشترك", "🎬 معالجة AI"])
    with main_tab1:
        current_otp = totp.now()
        st.success(f"🔑 الرمز الحالي:\n# **{current_otp}**")
    with main_tab2:
        st.write("رفع الجودة بواسطة Replicate GPU API")
else:
    st.write("رفع الجودة بواسطة Replicate GPU API")


# ==========================================
# 3. دالة المعالجة عبر Replicate
# ==========================================
def upscale_image_with_replicate(image_path):
    """
    إرسال الملف لـ Replicate وتطبيق Real-ESRGAN بذكاء اصطناعي حقيقي.
    """
    try:
        with open(image_path, "rb") as file:
            output = replicate.run(
                "nightmareai/real-esrgan:424308634d02e05f0217578351543716a5c1f5139097d81a8b0c4a4e157796d4",
                input={
                    "image": file,
                    "scale": 2,
                    "face_enhance": True,  # تحسين ملامح الوجه وتنقيتها
                },
            )
        return output
    except Exception as e:
        st.error(
            f"حدث خطأ أثناء الاتصال بـ Replicate: {e}\nتأكد من إضافة REPLICATE_API_TOKEN في Secrets بشكل صحيح."
        )
        return None


# ==========================================
# 4. الواجهة والرفع
# ==========================================
uploaded_file = st.file_uploader(
    "ارفع صورة لمعالجتها بالـ AI الخارجي:",
    type=["jpg", "png", "jpeg"],
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة الأصلية", use_column_width=True)

    if st.button("رفع الجودة بالـ AI الخارجي 🔥"):
        with st.spinner("جاري المعالجة بالسيرفر السريع ورفع الجودة..."):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".png"
            ) as tmp_file:
                image.save(tmp_file.name)
                result_url = upscale_image_with_replicate(tmp_file.name)

            if result_url:
                st.success("تمت المعالجة بنجاح عبر كرت الشاشة الخارجي!")
                st.image(
                    result_url,
                    caption="النتيجة بعد الـ AI",
                    use_column_width=True,
                )
