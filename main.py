import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from gui.app import RenamerApp


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


try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    root = tk.Tk()
    root.withdraw()  # يخفي النافذة الأساسية
    messagebox.showerror("خطأ", "تأكد إن pytesseract و pdf2image متنصبين")
    sys.exit()


if __name__ == "__main__":
    app = RenamerApp()
    app.mainloop()
