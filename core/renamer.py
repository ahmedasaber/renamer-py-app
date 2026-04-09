import os
import re

def build_new_name(ref):
    parts = [p.strip() for p in ref.split("/")]

    if len(parts) >= 8:
        name = f"{parts[1]} {parts[4]} {parts[6]} {parts[7]}.pdf"
        return "".join(c for c in name if c not in r'\/:*?"<>|')

    return None


def get_unique_path(folder, new_name):
    new_path = os.path.join(folder, new_name)
    counter = 1

    while os.path.exists(new_path):
        new_path = os.path.join(folder, new_name.replace(".pdf", f"_({counter}).pdf"))
        counter += 1

    return new_path


def already_renamed(filename):
    """
    بترجع True لو الملف اتسمّى قبل كده بالفورمات الصح
    QS GEN 373 REV00.pdf      → True  ⏭️
    QS GEN 373 REV00_(1).pdf  → True  ⏭️
    doc007376202604.pdf       → False ✅
    """
    name = os.path.splitext(filename)[0]
    name = re.sub(r'_\(\d+\)$', '', name)  # شيل _(1) أو _(2) لو موجود
    pattern = r'^[A-Z]{2,3}\s[A-Z]{2,4}\s\d+\sREV\d+$'
    return bool(re.match(pattern, name, re.IGNORECASE))