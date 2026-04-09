import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import pytesseract
from pdf2image import convert_from_path

from config.config import DEFAULT_TESSERACT, DEFAULT_POPPLER
from core.parser import extract_ref
from core.renamer import build_new_name, get_unique_path


# ══════════════════════════════════════════════
#  GUI
# ══════════════════════════════════════════════
class RenamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Renamer")
        self.geometry("780x620")
        self.resizable(True, True)
        self.configure(bg="#1e1e2e")

        self._build_ui()

    # ── بناء الـ UI ──────────────────────────
    def _build_ui(self):
        PAD = dict(padx=16, pady=8)

        # ── العنوان ──
        tk.Label(self, text="PDF Auto Renamer",
                 font=("Segoe UI", 18, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=(18, 4))
        tk.Label(self, text="بيعيد تسمية ملفات PDF تلقائياً من الـ Submittal Ref",
                 font=("Segoe UI", 10),
                 bg="#1e1e2e", fg="#a6adc8").pack(pady=(0, 14))

        # ── إطار الإعدادات ──
        cfg = tk.Frame(self, bg="#313244", bd=0)
        cfg.pack(fill="x", **PAD)

        def row(parent, label, default, browse_cmd=None):
            f = tk.Frame(parent, bg="#313244")
            f.pack(fill="x", padx=12, pady=6)
            tk.Label(f, text=label, width=14, anchor="w",
                     font=("Segoe UI", 10), bg="#313244", fg="#cdd6f4").pack(side="left")
            var = tk.StringVar(value=default)
            e = tk.Entry(f, textvariable=var, font=("Segoe UI", 10),
                         bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4",
                         relief="flat", bd=4)
            e.pack(side="left", fill="x", expand=True, ipady=4)
            if browse_cmd:
                tk.Button(f, text="…", command=lambda: browse_cmd(var),
                          font=("Segoe UI", 10), bg="#585b70", fg="#cdd6f4",
                          relief="flat", bd=0, padx=8,
                          activebackground="#7f849c",
                          cursor="hand2").pack(side="left", padx=(6, 0))
            return var

        self.folder_var = row(cfg, "مجلد الـ PDF", "", self._browse_folder)
        self.tesseract_var = row(cfg, "Tesseract", DEFAULT_TESSERACT)
        self.poppler_var = row(cfg, "Poppler bin", DEFAULT_POPPLER)

        # ── DPI + Dry Run ──
        opt = tk.Frame(cfg, bg="#313244")
        opt.pack(fill="x", padx=12, pady=(4, 10))

        tk.Label(opt, text="DPI", font=("Segoe UI", 10),
                 bg="#313244", fg="#cdd6f4").pack(side="left")
        self.dpi_var = tk.IntVar(value=150)
        tk.Spinbox(opt, from_=72, to=400, increment=50, textvariable=self.dpi_var,
                   width=5, font=("Segoe UI", 10),
                   bg="#45475a", fg="#cdd6f4", relief="flat",
                   buttonbackground="#585b70").pack(side="left", padx=(6, 20))

        self.dry_var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(opt, text="Dry Run (معاينة بس بدون تغيير)",
                            variable=self.dry_var,
                            font=("Segoe UI", 10),
                            bg="#313244", fg="#cdd6f4",
                            selectcolor="#45475a",
                            activebackground="#313244",
                            activeforeground="#cdd6f4")
        cb.pack(side="left")

        # ── زرار التشغيل ──
        self.run_btn = tk.Button(self, text="▶  ابدأ",
                                 command=self._start,
                                 font=("Segoe UI", 12, "bold"),
                                 bg="#89b4fa", fg="#1e1e2e",
                                 relief="flat", bd=0,
                                 padx=28, pady=8,
                                 activebackground="#74c7ec",
                                 cursor="hand2")
        self.run_btn.pack(pady=10)

        # ── Progress ──
        self.progress = ttk.Progressbar(self, mode="determinate", length=400)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TProgressbar", troughcolor="#313244",
                        background="#89b4fa", thickness=6)
        self.progress.pack(fill="x", padx=16, pady=(0, 6))

        self.status_var = tk.StringVar(value="جاهز")
        tk.Label(self, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg="#1e1e2e",
                 fg="#a6adc8").pack()

        # ── لوج ──
        log_frame = tk.Frame(self, bg="#1e1e2e")
        log_frame.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        self.log = tk.Text(log_frame,
                           font=("Cascadia Code", 10),
                           bg="#181825", fg="#cdd6f4",
                           relief="flat", bd=0,
                           wrap="word",
                           state="disabled")
        scroll = tk.Scrollbar(log_frame, command=self.log.yview,
                              bg="#313244", troughcolor="#1e1e2e")
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)

        # ألوان السطور
        self.log.tag_config("ok", foreground="#a6e3a1")
        self.log.tag_config("err", foreground="#f38ba8")
        self.log.tag_config("warn", foreground="#fab387")
        self.log.tag_config("info", foreground="#89b4fa")
        self.log.tag_config("header", foreground="#cba6f7")
        self.log.tag_config("muted", foreground="#6c7086")

    # ── Browse ──────────────────────────────
    def _browse_folder(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    # ── كتابة في اللوج ──────────────────────
    def _log(self, text, tag=""):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    # ── تشغيل في thread ──────────────────────
    def _start(self):
        folder = self.folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("تنبيه", "اختار مجلد صح أولاً")
            return

        self.run_btn.configure(state="disabled")
        self._clear_log()
        t = threading.Thread(target=self._process, daemon=True)
        t.start()

    def _process(self):
        folder = self.folder_var.get().strip()
        tesseract = self.tesseract_var.get().strip()
        poppler = self.poppler_var.get().strip()
        dpi = self.dpi_var.get()
        dry_run = self.dry_var.get()

        pytesseract.pytesseract.tesseract_cmd = tesseract

        pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        total = len(pdf_files)

        self._log(f"🗂  {total} ملف PDF", "header")
        self._log("=" * 44, "muted")

        self.progress["maximum"] = total
        self.progress["value"] = 0

        success = failed = 0

        for index, file in enumerate(pdf_files, 1):
            path = os.path.join(folder, file)
            self._log(f"\n[{index}/{total}]  📄  {file}", "info")
            self.status_var.set(f"جاري معالجة {index}/{total} ...")

            try:
                images = convert_from_path(
                    path,
                    first_page=1, last_page=1,
                    poppler_path=poppler,
                    dpi=dpi,
                    fmt='jpeg',
                    thread_count=2,
                )

                if not images:
                    self._log("         ⚠️  ملف فاضي", "warn")
                    failed += 1
                    self.progress["value"] = index
                    continue

                img = images[0]
                w, h = img.size
                cfg = r'--oem 1 --psm 6'

                crop = img.crop((0, 0, w, int(h * 0.20)))
                text = pytesseract.image_to_string(crop, lang='eng', config=cfg)
                ref = extract_ref(text)
                crop.close()

                if not ref:
                    crop2 = img.crop((0, 0, w, int(h * 0.40)))
                    text2 = pytesseract.image_to_string(crop2, lang='eng', config=cfg)
                    ref = extract_ref(text2)
                    crop2.close()

                img.close()

                if ref:
                    new_name = build_new_name(ref)
                    if new_name:
                        if new_name != file:
                            new_path = get_unique_path(folder, new_name)
                            if not dry_run:
                                os.rename(path, new_path)
                            label = "[DRY RUN]" if dry_run else "✅ تم"
                            self._log(f"         ✅  {new_name}  {label}", "ok")
                            success += 1
                        else:
                            self._log(f"         ⚠️  اتسمى قبل كدا الملف دا: {file}", "warn")
                            failed += 1
                    else:
                        self._log(f"         ⚠️  فورمات غريب: {ref}", "warn")
                        failed += 1
                else:
                    self._log("         ❌  مش لاقي Ref", "err")
                    failed += 1

            except Exception as e:
                self._log(f"         ❌  خطأ: {e}", "err")
                failed += 1

            self.progress["value"] = index

        self._log("\n" + "=" * 44, "muted")
        self._log(f"✅  نجح  : {success} ملف", "ok")
        self._log(f"❌  فشل  : {failed} ملف", "err")
        self._log("=" * 44, "muted")
        if dry_run:
            self._log("⚠️  Dry Run — مفيش حاجة اتغيرت فعلاً", "warn")
            self._log("    شيل علامة Dry Run واضغط ابدأ تاني لما تتأكد", "muted")

        self.status_var.set(f"خلص ✔  نجح {success} | فشل {failed}")
        self.run_btn.configure(state="normal")
