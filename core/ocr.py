import pytesseract


def extract_text_from_image(img, crop_percent=0.20):
    w, h = img.size
    cfg = r'--oem 1 --psm 6'

    crop = img.crop((0, 0, w, int(h * crop_percent)))
    text = pytesseract.image_to_string(crop, lang='eng', config=cfg)
    crop.close()
    return text
