import streamlit as st
import replicate
import os

# إعداد مفتاح API الخاص بـ Replicate (يفضل وضعه في st.secrets)
REPLICATE_API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN", "")

if not REPLICATE_API_TOKEN:
    st.warning("الرجاء إضافة REPLICATE_API_TOKEN في إعدادات Secrets الخاصة بـ Streamlit.")
else:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

st.title("رفع جودة الفيديو بال AI 🔥")

# رفع الفيديو
uploaded_file = st.file_uploader("قم برفع الفيديو هنا (صيغة MP4 أو MOV)", type=["mp4", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    if st.button("رفع جودة الفيديو بال AI 🔥"):
        if not REPLICATE_API_TOKEN:
            st.error("مفتاح API غير متاح. لا يمكن بدء المعالجة.")
        else:
            try:
                with st.spinner("جاري الاتصال بخوادم Replicate ومعالجة الفيديو... قد يستغرق الأمر بعض الوقت."):
                    # حفظ الفيديو المرفوع بشكل مؤقت ليتم إرساله للنموذج
                    temp_video_path = "temp_input_video.mp4"
                    with open(temp_video_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # ⚠️ تنبيه هام: هذا هو السطر الذي يسبب خطأ 404 إذا كان خاطئاً
                    # يجب استبدال النص أدناه بالمعرف الدقيق والإصدار للنموذج من موقع Replicate
                    # مثال لنموذج افتراضي (يجب تغييره حسب النموذج الذي تستخدمه):
                    MODEL_ID = "cjwbw/video-restoration:8d50b4a78a6ff68a41766cc6a04bfd9c12513f5d9cc00a120014eeebf552e4b3"
                    
                    # استدعاء النموذج
                    output = replicate.run(
                        MODEL_ID,
                        input={
                            "video": open(temp_video_path, "rb"),
                            # يمكنك إضافة أي معلمات أخرى يتطلبها النموذج هنا
                        }
                    )

                    st.success("تمت معالجة الفيديو بنجاح!")
                    
                    # عرض الفيديو الناتج (Replicate عادة ما يعيد رابط URL للفيديو)
                    st.video(output)
                    
            except replicate.exceptions.ReplicateError as e:
                st.error(f"حدث خطأ أثناء الاتصال بـ Replicate: {e}")
                st.info("💡 ملاحظة: خطأ 404 يعني أن معرف النموذج المكتوب في المتغير MODEL_ID غير صحيح أو تم حذفه. تأكد من نسخه بشكل صحيح من صفحة API الخاصة بالنموذج على Replicate.")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
            finally:
                # تنظيف الملف المؤقت
                if os.path.exists("temp_input_video.mp4"):
                    os.remove("temp_input_video.mp4")
