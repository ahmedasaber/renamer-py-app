import pytesseract
from core.parser import extract_ref


def get_ref_from_image(img):
    """
    بتجرب تستخرج الـ Ref من الصورة
    أول بأعلى 20% ، لو فشل بيجرب 40%
    """
    text = extract_text_from_image(img, 0.20)
    ref = extract_ref(text)

    if not ref:
        text = extract_text_from_image(img, 0.40)
        ref = extract_ref(text)

    return ref


def extract_text_from_image(img, crop_percent=0.20):
    w, h = img.size
    cfg = r'--oem 1 --psm 6'

    crop = img.crop((0, 0, w, int(h * crop_percent)))
    text = pytesseract.image_to_string(crop, lang='eng', config=cfg)
    crop.close()
    return text
