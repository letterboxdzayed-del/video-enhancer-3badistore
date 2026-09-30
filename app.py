import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

# 1. تحميل موديل الذكاء الاصطناعي
model = RRDBNet(
    num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2
)
upsampler = RealESRGANer(
    scale=2,
    model_path="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth",
    model=model,
    tile=400,  # لتخفيف الضغط على الذاكرة
    tile_pad=10,
    pre_pad=0,
    half=False,  # خليه False إذا السيرفر CPU بس
)


# 2. معالجة أي فريم أو صورة
def apply_ai_upscale(frame):
    output, _ = upsampler.enhance(frame, outscale=2)
    return output
