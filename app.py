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
    st.title("🔒 3badiJO")
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

st.title("⚡ 3badiJO Engine")

if st.session_state.is_admin:
    main_tab1, main_tab2 = st.tabs(["🔑 رمز المشترك", "🎬 معالجة الفيديو"])
    with main_tab1:
        current_otp = totp.now()
        st.success(f"🔑 الرمز الحالي:\n# **{current_otp}**")
    with main_tab2:
        st.write("تحسين الجودة والتشبع العالي")
else:
    st.write("تحسين الجودة والتشبع العالي")


# ==========================================
# 3. محرك الجودة القوية والتشبّع العالي (Rich Vibrant Engine)
# ==========================================
def pro_vibrant_enhance(frame):
    """رفع الجودة وتفاصيل الفيديو مع تشبع ألوان عالي وواضح جداً."""
    # 1. فلتر إبراز التفاصيل والحدّة النظيفة (Bilateral Filtering)
    detailed = cv2.bilateralFilter(frame, d=5, sigmaColor=50, sigmaSpace=50)

    # 2. إضافة حدّة متباينة خفيفة للحواف فقط
    edge_detail = cv2.addWeighted(frame, 1.5, detailed, -0.5, 0)

    # 3. رفع التشبّع العالي للألوان (Vibrance & Saturation Boost 40%)
    hsv = cv2.cvtColor(edge_detail, cv2.COLOR_BGR2HSV).astype(np.float32)

    # رفع التشبّع الغني
    hsv[:, :, 1] *= 1.40
    # ضبط الإضاءة خفيف لعدم البهتان
    hsv[:, :, 2] *= 1.05

    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    vibrant_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # 4. تعديل التباين الخفيف لإبراز عمق الألوان (Gamma Adjustment)
    lookUpTable = np.empty((1, 256), np.uint8)
    for i in range(256):
        lookUpTable[0, i] = np.clip(pow(i / 255.0, 0.90) * 255.0, 0, 255)

    return cv2.LUT(vibrant_bgr, lookUpTable)


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
        quality=7,
        pixelformat="yuv420p",
        ffmpeg_params=["-preset", "ultrafast"],
        macro_block_size=1,
    )

    progress_bar = st.progress(0)
    status_text = st.empty()
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_bgr = pro_vibrant_enhance(frame)
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

        writer.append_data(processed_rgb)
        frame_count += 1

        # تحديث كل ثانية (كل 30 فريم)
        if total_frames > 0 and frame_count % 30 == 0:
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
# 4. الواجهة
# ==========================================
uploaded_file = st.file_uploader(
    "ارفع فيديو أو صورة:", type=["mp4", "mov", "jpg", "png"]
)

if uploaded_file is not None:
    is_video = uploaded_file.name.split(".")[-1].lower() in ["mp4", "mov"]

    if is_video:
        st.video(uploaded_file)
        if st.button("تحسين الجودة 🔥"):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_file.read())

            output_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ).name

            with st.spinner("جاري معالجة الفيديو..."):
                enhance_video(tfile.name, output_file)

            st.success("تمت المعالجة بنجاح!")
            st.video(output_file)

            with open(output_file, "rb") as f:
                st.download_button(
                    "📥 تحميل الفيديو المحسن (MP4)",
                    f,
                    file_name="3badiJO_4K.mp4",
                    mime="video/mp4",
                )

    else:
        image = Image.open(uploaded_file)
        img_array = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        enhanced_bgr = pro_vibrant_enhance(img_bgr)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        st.subheader("مقارنة الجودة:")
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="قبل", use_column_width=True)
        with col2:
            st.image(enhanced_rgb, caption="بعد", use_column_width=True)
