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
        st.write("أدخل رمز الوصول المؤقت الخاص بك:")
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

st.title("⚡ 3badiJO Engine | VIP 4K Enhancement")

if st.session_state.is_admin:
    main_tab1, main_tab2 = st.tabs(
        ["🔑 رمز المشترك المتجدد (OTP)", "🎬 معالجة الفيديوهات والصور"]
    )
    with main_tab1:
        st.subheader("لوحة المؤسس - الرمز الحالي للمشتركين")
        current_otp = totp.now()
        st.success(f"🔑 الباسورد الحالي للمشتركين هو:\n# **{current_otp}**")
        st.info("الرمز يتغير تلقائياً كل 5 دقائق.")
    with main_tab2:
        st.write("استخدم المحرك لتعديل ومعالجة الفيديوهات والصور:")
else:
    st.write(
        "رفع الجودة، معالجة البشرة، حماية المناطق المعتمة من التشويش، والحفاظ على الصوت والألوان الأصلية."
    )


# ==========================================
# 3. محرك المعالجة الذكي للوجه والألوان والحدّة
# ==========================================
def smart_enhance_frame(frame, apply_cc=True):
    """شاربين قوي للوجه والبشرة + تنعيم وتقليل النويز بالخلفية والظلال."""

    # 1. تحويل الصورة لمساحة ألوان YCrCb للتعرف على درجة لون البشرة والسطوع
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)

    # قناع استهداف البشرة (Skin Mask)
    skin_mask = cv2.inRange(ycrcb, (0, 133, 77), (255, 173, 127))
    skin_mask = cv2.GaussianBlur(skin_mask, (9, 9), 0) / 255.0

    # قناع المناطق المظلمة (Shadows Mask)
    shadow_mask = np.where(y < 60, 1.0, 0.0)
    shadow_mask = cv2.GaussianBlur(shadow_mask.astype(np.float32), (15, 15), 0)

    # 2. تحسين الحدة (Sharpness) الموجهة
    gaussian = cv2.GaussianBlur(frame, (0, 0), 2.0)
    high_sharp = cv2.addWeighted(frame, 2.2, gaussian, -1.2, 0)  # حدّة قوية للوجه
    soft_frame = cv2.fastNlMeansDenoisingColored(
        frame, None, 3, 3, 7, 21
    )  # تنعيم خفيف للمناطق المعتمة

    # 3. دمج الحدة حسب المنطقة (بشرة/خلفية/ظلال)
    skin_mask_3ch = cv2.merge([skin_mask, skin_mask, skin_mask])
    shadow_mask_3ch = cv2.merge([shadow_mask, shadow_mask, shadow_mask])

    # تطبيق الشاربين القوي على البشرة والشاربين المعتدل لباقي التفاصيل
    enhanced = frame * (1.0 - skin_mask_3ch) + high_sharp * skin_mask_3ch

    # تقليل النويز بالمناطق المعتمة
    enhanced = enhanced * (1.0 - shadow_mask_3ch) + soft_frame * shadow_mask_3ch
    enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)

    # 4. تحسين الألوان المحافظ (Vibrance & Color Grading)
    if apply_cc:
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV).astype(np.float32)
        # رفع التشبّع بنسبة معتدلة بدون إتلاف الألوان الأصلية
        hsv[:, :, 1] *= 1.15
        hsv[:, :, 2] *= 1.05
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return enhanced


def process_video_with_audio(input_path, output_path, apply_cc=True):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0 or fps is None:
        fps = 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    new_w, new_h = width * 2, height * 2

    # فيديو مؤقت بدون صوت
    temp_no_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    writer = imageio.get_writer(
        temp_no_audio,
        fps=fps,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
    )

    progress_bar = st.progress(0)
    status_text = st.empty()

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        resized_frame = cv2.resize(
            frame, (new_w, new_h), interpolation=cv2.INTER_CUBIC
        )
        processed_bgr = smart_enhance_frame(resized_frame, apply_cc=apply_cc)
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

        writer.append_data(processed_rgb)

        frame_count += 1
        if total_frames > 0:
            progress = int((frame_count / total_frames) * 100)
            progress_bar.progress(min(progress, 100))
        status_text.text(f"جاري معالجة الفريمات: {frame_count}/{total_frames}")

    cap.release()
    writer.close()

    # دمج الصوت الأصلي مع الفيديو الجديد باستعمال imageio-ffmpeg
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
        # في حال عدم وجود مسار صوت بالفيديو الأصلي
        os.replace(temp_no_audio, output_path)


# ==========================================
# 4. خيارات رفع ومعالجة الملفات
# ==========================================
mode = st.radio(
    "اختر خيار التعديل:", ["تحسين جودة 4K ذكي", "4K ذكي + تحسين ألوان سينمائي"]
)
uploaded_file = st.file_uploader(
    "ارفع فيديو أو صورة للتعديل:", type=["mp4", "mov", "jpg", "png"]
)

if uploaded_file is not None:
    is_video = uploaded_file.name.split(".")[-1].lower() in ["mp4", "mov"]
    apply_cc = mode == "4K ذكي + تحسين ألوان سينمائي"

    if is_video:
        st.video(uploaded_file)
        if st.button("بدء معالجة الفيديو 🔥"):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_file.read())

            output_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ).name

            with st.spinner(
                "جاري تحسين الجودة، ضبط حدّة الوجه، حماية الخلفيات، ودمج الصوت..."
            ):
                process_video_with_audio(tfile.name, output_file, apply_cc=apply_cc)

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

        h, w = img_bgr.shape[:2]
        resized_img = cv2.resize(
            img_bgr, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC
        )
        enhanced_bgr = smart_enhance_frame(resized_img, apply_cc=apply_cc)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        st.subheader("مقارنة الجودة (قبل / بعد):")
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="الصورة الأصلية", use_column_width=True)
        with col2:
            st.image(
                enhanced_rgb,
                caption="بعد التعديل والـ 4K",
                use_column_width=True,
            )
