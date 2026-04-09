import sys
import subprocess

# ── إخفاء كل console subprocesses على Windows ──
if sys.platform == "win32":
    _orig_popen = subprocess.Popen.__init__


    def _hidden_popen(self, *args, **kwargs):
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs.setdefault("startupinfo", si)
        _orig_popen(self, *args, **kwargs)
    subprocess.Popen.__init__ = _hidden_popen


import tkinter as tk
from tkinter import messagebox
from config.config import DEFAULT_TESSERACT, DEFAULT_POPPLER
from gui.app import RenamerApp

try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    root = tk.Tk()
    root.withdraw()  # يخفي النافذة الأساسية
    messagebox.showerror("خطأ", "تأكد إن pytesseract و pdf2image متنصبين")
    sys.exit()

# def check_dependencies():
#     if not os.path.exists(DEFAULT_TESSERACT):
#         root1 = tk.Tk()
#         root1.withdraw()
#         messagebox.showerror("خطأ", "❌ Tesseract مش موجود في الفولدر")
#         sys.exit()
#
#     if not os.path.exists(DEFAULT_POPPLER):
#         root1 = tk.Tk()
#         root1.withdraw()
#         messagebox.showerror("خطأ", "❌ Poppler مش موجود في الفولدر")
#         sys.exit()


if __name__ == "__main__":
    # check_dependencies()
    app = RenamerApp()
    app.mainloop()
