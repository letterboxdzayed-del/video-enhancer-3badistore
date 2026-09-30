import os
import tempfile
import cv2
import imageio
import numpy as np
import pyotp
import streamlit as st
from PIL import Image

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(
    page_title="3badiJO Engine - VIP 4K",
    page_icon="🎬",
    layout="centered",
)

# ==========================================
# 2. نظام الأمان والمفتاح السرّي
# ==========================================
ADMIN_PASSWORD = "zayed321abadi"
USER_SECRET = "JBSWY3DPEHPK3PXP"
totp = pyotp.TOTP(USER_SECRET, interval=300)  # 5 دقائق

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
# 3. لوحة المؤسس والواجهة
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
        st.info(
            "أعط هذا الرمز للمشترك ليدخل به من تبويب المشتركين. ينتهي الرمز وتتغير قيمته تلقائياً كل 5 دقائق."
        )
    with main_tab2:
        st.write("استخدم المحرك لتعديل ومعالجة الفيديوهات والصور:")
else:
    st.write(
        "رفع الجودة، ضبط الإضاءة والتباين تلقائياً مع تنعيم الانتقالات، وتطبيق الفلاتر السينمائية."
    )


# ==========================================
# 4. محرك تحسين الفريمات والانتقال الناعم (Smooth Adjustment)
# ==========================================
def enhance_frame(
    frame, apply_cc=True, target_sharpness=1.8, clip_limit=2.8, alpha_fade=1.0
):
    """تحسين الجودة والحدّة والتباين مع دعم التنعيم التدريجي (Fade)."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # دمج التباين القديم والجديد بنعومة إذا لزم
    cl = cv2.addWeighted(cl, alpha_fade, l, 1.0 - alpha_fade, 0)

    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # حدّة ممتازة لتوضيح التفاصيل
    gaussian_3 = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.0)
    sharpened = cv2.addWeighted(
        enhanced_bgr, 1.0 + target_sharpness, gaussian_3, -target_sharpness, 0
    )

    if apply_cc:
        sharpened = sharpened.astype(np.float32)
        sharpened[:, :, 2] *= 1.12  # تعزيز اللون الأحمر/الدافئ
        sharpened[:, :, 1] *= 1.03
        sharpened[:, :, 0] *= 0.92
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    return sharpened


def process_video_smart(input_path, output_path, apply_cc=True):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0 or fps is None:
        fps = 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    new_w, new_h = width * 2, height * 2

    # تجهيز كاتب الفيديو عبر imageio بترميز H.264
    writer = imageio.get_writer(
        output_path, fps=fps, codec="libx264", quality=8, pixelformat="yuv420p"
    )

    progress_bar = st.progress(0)
    status_text = st.empty()

    frame_count = 0
    interval = 5  # تحديث التباين كل 5 فريمات
    current_clip_limit = 2.8
    target_clip_limit = 2.8

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        resized_frame = cv2.resize(
            frame, (new_w, new_h), interpolation=cv2.INTER_CUBIC
        )

        # تحسين التباين كل 5 فريمات والتعديل التدريجي (Fade) بينها
        step_in_interval = frame_count % interval
        if step_in_interval == 0:
            gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
            mean_brightness = np.mean(gray)
            # احتساب التباين بناءً على سطوع الفريم
            if mean_brightness < 80:
                target_clip_limit = 3.2
            elif mean_brightness > 180:
                target_clip_limit = 2.0
            else:
                target_clip_limit = 2.7

        # الانتقال التدريجي الناعم (Fade Transition)
        alpha = (step_in_interval + 1) / float(interval)
        active_clip_limit = (
            1 - alpha
        ) * current_clip_limit + alpha * target_clip_limit

        if step_in_interval == interval - 1:
            current_clip_limit = target_clip_limit

        processed_bgr = enhance_frame(
            resized_frame, apply_cc=apply_cc, clip_limit=active_clip_limit
        )

        # تحويل BGR إلى RGB الحقيقي للعرض بالفيديو
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)
        writer.append_data(processed_rgb)

        frame_count += 1
        if total_frames > 0:
            progress = int((frame_count / total_frames) * 100)
            progress_bar.progress(min(progress, 100))
        status_text.text(f"جاري معالجة الفريمات: {frame_count}/{total_frames}")

    cap.release()
    writer.close()


# ==========================================
# 5. واجهة المعالجة
# ==========================================
mode = st.radio("اختر خيار التعديل:", ["تحسين جودة 4K فقط", "4K + فلتر سينمائي"])
uploaded_file = st.file_uploader(
    "ارفع فيديو أو صورة للتعديل:", type=["mp4", "mov", "jpg", "png"]
)

if uploaded_file is not None:
    is_video = uploaded_file.name.split(".")[-1].lower() in ["mp4", "mov"]
    apply_cc = mode == "4K + فلتر سينمائي"

    if is_video:
        st.video(uploaded_file)
        if st.button("بدء معالجة الفيديو 🔥"):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_file.read())

            output_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ).name

            with st.spinner("جاري رفع الجودة وتطبيق الانتقال الناعم للفريمات..."):
                process_video_smart(tfile.name, output_file, apply_cc=apply_cc)

            st.success("تمت المعالجة بنجاح! شاهد أو حمل الفيديو المحسن:")
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

        h, w = img_bgr.shape[:2]
        resized_img = cv2.resize(
            img_bgr, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC
        )
        enhanced_bgr = enhance_frame(resized_img, apply_cc=apply_cc)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        st.subheader("مقارنة الجودة (قبل / بعد):")
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="الصورة الأصلية", use_column_width=True)
        with col2:
            st.image(
                enhanced_rgb,
                caption="بعد تحسين الجودة والـ 4K",
                use_column_width=True,
            )
