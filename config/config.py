# ══════════════════════════════════════════════
#  CONFIG — عدّل المسارات دي
# ══════════════════════════════════════════════
#DEFAULT_TESSERACT = r'E:\renamer\Tesseract-OCR\tesseract.exe'
#DEFAULT_POPPLER   = r'E:\renamer\poppler-25.12.0\Library\bin'

import os
import sys


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)  # لما يبقى exe
    return os.path.dirname(os.path.abspath(__file__))  # لما يبقى script


BASE_DIR = get_base_dir()

DEFAULT_TESSERACT = os.path.join(BASE_DIR, "Tesseract-OCR", "tesseract.exe")
DEFAULT_POPPLER = os.path.join(BASE_DIR, "poppler-25.12.0", "Library", "bin")