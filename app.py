import os
import tempfile
import time
import cv2
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
# 2. نظام الأمان (OTP متجدد كل 5 دقائق)
# ==========================================
# المفتاح السري الخاص بالعميل (تنشئ واحد لكل مشترِ)
USER_SECRET = "JBSWY3DPEHPK3PXP"
totp = pyotp.TOTP(USER_SECRET, interval=300)  # 300 ثانية = 5 دقائق

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def check_auth():
    st.title("🔒 3badiJO - بوابة المشتركين")
    st.write("أدخل رمز الوصول المؤقت الخاص بك (يتغير تلقائياً كل 5 دقائق):")

    user_code = st.text_input("رمز الـ OTP:", type="password")

    if st.button("دخول المنصة"):
        if totp.verify(user_code):
            st.session_state.authenticated = True
            st.success("تم التوثيق بنجاح!")
            st.rerun()
        else:
            st.error("الرمز غير صحيح أو انتهت صلاحية الخمس دقائق!")


if not st.session_state.authenticated:
    check_auth()
    st.stop()


# ==========================================
# 3. محرك المعالجة الذكي (Smart Frame Engine)
# ==========================================
def enhance_frame(frame, apply_cc=True, target_sharpness=1.5):
    """تحسين الجودة والتباين والحدّة للفريم الواحد."""
    # 1. تحويل لـ LAB لضبط الإضاءة بدون تخريب الألوان
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # 2. تطبيق CLAHE (موازن التباين الذكي)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # 3. فلتر الحدة والتفاصيل السينمائية (Unsharp Masking)
    gaussian_3 = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.0)
    sharpened = cv2.addWeighted(
        enhanced_bgr, 1.0 + target_sharpness, gaussian_3, -target_sharpness, 0
    )

    # 4. تطبيق الفلتر السينمائي (إذا تم اختياره)
    if apply_cc:
        # لمسة ألوان سينمائية دافئة وثابتة (Warm Cinematic Tint)
        sharpened = sharpened.astype(np.float32)
        sharpened[:, :, 2] *= 1.08  # BGR: زيادة الأحمر قليلاً
        sharpened[:, :, 1] *= 1.02  # BGR: زيادة الأخضر قليلاً
        sharpened[:, :, 0] *= 0.95  # BGR: تقليل الأزرق الداكن
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    return sharpened


def process_video(input_path, output_path, apply_cc=True):
    """معالجة الفيديو وتعديل التباين والإضاءة كل 5 فريمات."""
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # مضاعفة الدقة للـ 4K / HD
    new_w, new_h = width * 2, height * 2

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (new_w, new_h))

    progress_bar = st.progress(0)
    status_text = st.empty()

    frame_count = 0
    cached_settings = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # تكبير الفريم مضاعف لمزيد من الوضوح
        resized_frame = cv2.resize(
            frame, (new_w, new_h), interpolation=cv2.INTER_CUBIC
        )

        # حساب وتحسين كل 5 فريمات لتوفير الأداء والذكاء
        if frame_count % 5 == 0:
            processed_frame = enhance_frame(resized_frame, apply_cc=apply_cc)
            cached_settings = processed_frame
        else:
            processed_frame = enhance_frame(resized_frame, apply_cc=apply_cc)

        out.write(processed_frame)
        frame_count += 1

        # تحديث شريط التقدم
        progress = int((frame_count / total_frames) * 100)
        progress_bar.progress(progress)
        status_text.text(f"جاري معالجة الفريمات: {frame_count}/{total_frames}")

    cap.release()
    out.release()


# ==========================================
# 4. الواجهة الرئيسية للبرنامج
# ==========================================
st.sidebar.success("🟢 أهلاً بك في المحرك الخاص")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()

st.title("⚡ 3badiJO Engine | VIP 4K Enhancement")
st.write(
    "رفع الجودة، ضبط الإضاءة والتباين تلقائياً كل 5 فريمات، وتطبيق الفلاتر السينمائية."
)

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

            with st.spinner("جاري تحليل الجودة وضبط الفريمات..."):
                process_video(tfile.name, output_file, apply_cc=apply_cc)

            st.success("تمت المعالجة بنجاح! شاهد أو حمل الفيديو المحسن:")
            st.video(output_file)

            with open(output_file, "rb") as f:
                st.download_button(
                    "📥 تحميل الفيديو المحسن", f, file_name="3badiJO_4K.mp4"
                )

    else:
        # لمعالجة الصور فوراً
        image = Image.open(uploaded_file)
        img_array = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # مضاعفة الحجم وتحسين الجودة
        h, w = img_bgr.shape[:2]
        resized_img = cv2.resize(
            img_bgr, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC
        )
        enhanced_img = enhance_frame(resized_img, apply_cc=apply_cc)

        enhanced_rgb = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB)

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
