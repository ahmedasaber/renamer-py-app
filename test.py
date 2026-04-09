# import pytesseract
# from pdf2image import convert_from_path
# import os
#
# # 1. مسار تيسيراكت
# pytesseract.pytesseract.tesseract_cmd = r'E:\renamer\Tesseract-OCR\tesseract.exe'
#
# # 2. مسار الفولدر اللي فيه ملفات الـ PDF
# folder = r"E:\RENAME - Copy"
#
# # 3. المسار الجديد لـ Poppler (عدله بناءً على مكان الـ .exe اللي قولتلك عليه)
# poppler_path = r'E:\renamer\poppler-25.12.0\Library\bin'
#
# # اختبار سريع للمسار قبل البدء
# if not os.path.exists(poppler_path):
#     print(f"❌ تحذير: مسار Poppler غير صحيح: {poppler_path}")
# else:
#     print(f"✅ مسار Poppler مضبوط.. جاري معالجة الملفات...")
#
# for file in os.listdir(folder):
#     if file.endswith(".pdf"):
#         path = os.path.join(folder, file)
#
#         try:
#             # تحويل الصفحة الأولى بصيغة PIL Image
#             images = convert_from_path(path, first_page=1, last_page=1, poppler_path=poppler_path)
#
#             if not images:
#                 continue
#
#             # استخراج النص
#             text = pytesseract.image_to_string(images[0])
#             lines = [line.strip() for line in text.split("\n") if line.strip()]
#             print(lines)
#             # البحث عن السطر المطلوب
#             ref_line = next(
#                 (l for l in lines if "SUBMITTAL" in l.upper() and "REF" in l.upper()),
#                 None
#             )
#
#             if ref_line:
#                 # تقسيم السطر (تأكد من شكل الـ Slash في ملفاتك)
#                 parts = [p.strip() for p in ref_line.split("/")]
#                 print(parts)
#
#                 if len(parts) >= 8:
#                     # تنظيف الاسم الجديد من أي حروف ممنوعة في الويندوز
#                     new_name = f"{parts[1]}_{parts[4]}_{parts[6]}_{parts[7]}.pdf"
#                     new_name = "".join(i for i in new_name if i not in r'\/:*?"<>|')
#
#                     new_path = os.path.join(folder, new_name)
#
#                     # إغلاق الصورة قبل تغيير الاسم لضمان عدم حدوث PermissionError
#                     images[0].close()
#
#                     os.rename(path, new_path)
#                     print(f"✅ تم التغيير: {file} -> {new_name}")
#                 else:
#                     print(f"⚠️ السطر موجود بس التقسيم (/) مش كافي: {file}")
#             else:
#                 print(f"🔍 لم يتم العثور على الكلمة داخل: {file}")
#
#         except Exception as e:
#             print(f"❌ خطأ في الملف {file}: {e}")

# import pytesseract
# from pdf2image import convert_from_path
# import os
# import re
#
# pytesseract.pytesseract.tesseract_cmd = r'E:\renamer\Tesseract-OCR\tesseract.exe'
# folder = r"E:\RENAME - Copy"
# poppler_path = r'E:\renamer\poppler-25.12.0\Library\bin'
#
# DRY_RUN = False  # غيّرها False لما تتأكد
#
#
# def fix_rev_zeros(ref):
#     # بيصلح الـ O → 0 في الأرقام بعد REV بس
#     # مثال: REV0O → REV00 ، REVO1 → REV01
#     def replace_in_rev(match):
#         return match.group(0).replace("O", "0").replace("o", "0")
#
#     return re.sub(r'REV[0-9O]+', replace_in_rev, ref, flags=re.IGNORECASE)
#
#
# def extract_ref(text):
#     pattern = r'\d{3,4}/[A-Z]{2,3}/[A-Z]+/[A-Z]+/[A-Z]+/\d+/\d+/REV\d+'
#     match = re.search(pattern, text, re.IGNORECASE)
#     if match:
#         return fix_rev_zeros(match.group(0))
#
#     lines = [line.strip() for line in text.split("\n") if line.strip()]
#     for i, line in enumerate(lines):
#         if "SUBMITTAL" in line.upper() and "REF" in line.upper():
#             inline = re.search(r'[\w]+/[\w/]+', line)
#             if inline and inline.group(0).count('/') >= 5:
#                 return fix_rev_zeros(inline.group(0))
#             if i + 1 < len(lines):
#                 next_line = lines[i + 1]
#                 if '/' in next_line and next_line.count('/') >= 5:
#                     return fix_rev_zeros(next_line)  # ← وهنا
#     return None
#
# def build_new_name(ref):
#     parts = [p.strip() for p in ref.split("/")]
#     if len(parts) >= 8:
#         new_name = f"{parts[1]} {parts[4]} {parts[6]} {parts[7]}.pdf"
#         return "".join(c for c in new_name if c not in r'\/:*?"<>|')
#     return None
#
# def get_unique_path(folder, new_name):
#     new_path = os.path.join(folder, new_name)
#     counter = 1
#     while os.path.exists(new_path):
#         new_path = os.path.join(folder, new_name.replace(".pdf", f"_{counter}.pdf"))
#         counter += 1
#     return new_path
#
# # ============================================================
# pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
# total = len(pdf_files)
#
# print(f"🗂 {total} ملف PDF")
# print("=" * 40)
#
# success = 0
# failed = 0
#
# for index, file in enumerate(pdf_files, 1):
#     path = os.path.join(folder, file)
#
#     # ── سطر العنوان ─────────────────────────────
#     print(f"\n[{index}/{total}] 📄 {file}")
#
#     try:
#         images = convert_from_path(
#             path,
#             first_page=1, last_page=1,
#             poppler_path=poppler_path,
#             dpi=150,
#             fmt='jpeg',
#             thread_count=2
#         )
#
#         if not images:
#             print(f"         ⚠️  ملف فاضي")
#             failed += 1
#             continue
#
#         img = images[0]
#         width, height = img.size
#
#         # Crop أعلى 20% أولاً
#         header_crop = img.crop((0, 0, width, int(height * 0.20)))
#         custom_config = r'--oem 1 --psm 6'
#         text = pytesseract.image_to_string(header_crop, lang='eng', config=custom_config)
#         ref = extract_ref(text)
#
#         # Fallback: أعلى 40%
#         if not ref:
#             bigger_crop = img.crop((0, 0, width, int(height * 0.40)))
#             text2 = pytesseract.image_to_string(bigger_crop, lang='eng', config=custom_config)
#             ref = extract_ref(text2)
#             bigger_crop.close()
#
#         header_crop.close()
#         img.close()
#
#         if ref:
#             new_name = build_new_name(ref)
#             if new_name:
#                 new_path = get_unique_path(folder, new_name)
#                 if DRY_RUN:
#                     print(f"         ✅  {new_name}  [DRY RUN]")
#                 else:
#                     os.rename(path, new_path)
#                     print(f"         ✅  {new_name}")
#                 success += 1
#             else:
#                 print(f"         ⚠️  فورمات غريب: {ref}")
#                 failed += 1
#         else:
#             # ── اطبع النص اللي اتقرأ عشان تعرف المشكلة ──
#             print(f"         ❌  مش لاقي Ref")
#             print(f"         🔎  النص اللي اتقرأ: {text[:120].strip()!r}")
#             failed += 1
#
#     except Exception as e:
#         print(f"         ❌  خطأ: {e}")
#         failed += 1
#
# # ── ملخص نهائي ──────────────────────────────
# print("\n" + "=" * 40)
# print(f"✅  نجح  : {success} ملف")
# print(f"❌  فشل  : {failed} ملف")
# print("=" * 40)
# if DRY_RUN:
#     print("⚠️  DRY RUN - مفيش حاجة اتغيرت فعلاً")
#     print("    غيّر DRY_RUN = False لما تتأكد")