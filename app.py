import os
import subprocess
import tempfile
import cv2
import imageio
import numpy as np
import pyotp
import streamlit as st
from PIL import Image

# ==========================================
# 1. إعدادات الصفحة والأمان
# ==========================================
st.set_page_config(
    page_title="3badiJO Engine - VIP 4K",
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
    st.title("🔒 3badiJO - بوابة الوصول")
    tab1, tab2 = st.tabs(["دخول المشتركين 👤", "لوحة المؤسس 👑"])

    with tab1:
        st.write("أدخل رمز الوصول الخاص بك:")
        user_code = st.text_input(
            "رمز الـ OTP للمشتركين:", type="password", key="user_input"
        )
        if st.button("دخول المنصة", key="btn_user"):
            if totp.verify(user_code):
                st.session_state.authenticated = True
                st.session_state.is_admin = False
                st.success("تم التوثيق بنجاح!")
                st.rerun()
            else:
                st.error("الرمز غير صحيح أو انتهت صلاحيته!")

    with tab2:
        st.write("تسجيل دخول مالك الموقع:")
        admin_pass = st.text_input(
            "كلمة سر المؤسس:", type="password", key="admin_input"
        )
        if st.button("دخول كـ مؤسس", key="btn_admin"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.success("أهلاً بك زايد!")
                st.rerun()
            else:
                st.error("كلمة سر المؤسس غير صحيحة!")


if not st.session_state.authenticated:
    check_auth()
    st.stop()

# ==========================================
# 2. الواجهة الرئيسية
# ==========================================
st.sidebar.success(
    "🟢 أهلاً بك"
    + (" (المؤسس)" if st.session_state.is_admin else " (مشترك)")
)
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.rerun()

st.title("⚡ 3badiJO Engine | Ultra Cinema 4K")

if st.session_state.is_admin:
    main_tab1, main_tab2 = st.tabs(
        ["🔑 رمز المشترك المتجدد (OTP)", "🎬 معالجة الفيديو والصور"]
    )
    with main_tab1:
        st.subheader("لوحة المؤسس - الرمز الحالي للمشتركين")
        current_otp = totp.now()
        st.success(f"🔑 الباسورد الحالي للمشتركين هو:\n# **{current_otp}**")
        st.info("الرمز يتغير تلقائياً كل 5 دقائق.")
    with main_tab2:
        st.write("ارفع الملف لمعالجته فوراً برفع الجودة والألوان:")
else:
    st.write("محرك تحسين الجودة والحدّة وضبط الألوان السينمائية.")


# ==========================================
# 3. خوارزمية التعديل السينمائي الملحوظ (Ultra VIP Filter)
# ==========================================
def process_frame(frame):
    """تحسين حقيقي وملموس للجودة والتباين والألوان بدون نويز مزعج."""

    # 1. رفع الدقة للضعف
    h, w = frame.shape[:2]
    resized = cv2.resize(frame, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # 2. تعزيز التباين وإبراز التفاصيل عبر مساحة ألوان LAB
    lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # 3. تطبيق Sharpening ذكي متوازن إبراز ملامح الشخص
    blur = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.5)
    sharp = cv2.addWeighted(enhanced_bgr, 1.45, blur, -0.45, 0)

    # 4. تحسين الألوان بنمط سينمائي فخم (Vibrance & Color Pop)
    hsv = cv2.cvtColor(sharp, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] *= 1.22  # رفع التشبّع لتوضيح الألوان
    hsv[:, :, 2] *= 1.05  # رفع السطوع الخفيف
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)

    final_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return final_bgr


def enhance_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0 or fps is None:
        fps = 30

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    temp_no_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    writer = imageio.get_writer(
        temp_no_audio,
        fps=fps,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        macro_block_size=1,
    )

    progress_bar = st.progress(0)
    status_text = st.empty()
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_bgr = process_frame(frame)
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

        writer.append_data(processed_rgb)
        frame_count += 1

        if total_frames > 0 and frame_count % 3 == 0:
            progress = int((frame_count / total_frames) * 100)
            progress_bar.progress(min(progress, 100))
            status_text.text(f"جاري معالجة الفريمات: {frame_count}/{total_frames}")

    cap.release()
    writer.close()

    # دمج الصوت الأصلي
    try:
        import imageio_ffmpeg

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe,
            "-y",
            "-i",
            temp_no_audio,
            "-i",
            input_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0?",
            output_path,
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        os.replace(temp_no_audio, output_path)


# ==========================================
# 4. الواجهة المباشرة
# ==========================================
uploaded_file = st.file_uploader(
    "ارفع فيديو أو صورة للتعديل:", type=["mp4", "mov", "jpg", "png"]
)

if uploaded_file is not None:
    is_video = uploaded_file.name.split(".")[-1].lower() in ["mp4", "mov"]

    if is_video:
        st.video(uploaded_file)
        if st.button("بدء تحسين الجودة 🔥"):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_file.read())

            output_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ).name

            with st.spinner("جاري تطبيق المعالجة السينمائية وحفظ الصوت..."):
                enhance_video(tfile.name, output_file)

            st.success("تمت المعالجة بنجاح!")
            st.video(output_file)

            with open(output_file, "rb") as f:
                st.download_button(
                    "📥 تحميل الفيديو المحسن (MP4)",
                    f,
                    file_name="3badiJO_4K_Pro.mp4",
                    mime="video/mp4",
                )

    else:
        image = Image.open(uploaded_file)
        img_array = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        enhanced_bgr = process_frame(img_bgr)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        st.subheader("مقارنة الجودة (قبل / بعد):")
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="الصورة الأصلية", use_column_width=True)
        with col2:
            st.image(
                enhanced_rgb,
                caption="بعد التعديل السينمائي",
                use_column_width=True,
            )
