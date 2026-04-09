# PDF Auto Renamer

بيعيد تسمية ملفات PDF تلقائياً عن طريق قراءة الـ **Submittal Ref** من أول صفحة باستخدام OCR.

```
doc0073762026040909418.pdf  →  QS GEN 373 REV00.pdf
doc0073762026040909411.pdf  →  CPR STR 1742 REV00.pdf
```

---

## المتطلبات

### Python packages
```bash
pip install pytesseract pdf2image Pillow
```

### برامج خارجية (مطلوبة)

| البرنامج | الاستخدام | التحميل |
|----------|-----------|---------|
| **Tesseract OCR** | قراءة النص من الصور | [github.com/UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) |
| **Poppler** | تحويل PDF لصور | [github.com/oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) |

---

## هيكل المشروع

```
renamer/
│
├── main.py                  ← نقطة التشغيل
│
├── config/
│   └── config.py            ← مسارات Tesseract و Poppler
│
├── core/
│   ├── parser.py            ← استخراج الـ Ref من النص
│   └── renamer.py           ← بناء الاسم الجديد
│
├── gui/
│   └── app.py               ← واجهة المستخدم (tkinter)
│
└── README.md
```

---

## الإعداد

### 1. عدّل مسارات البرامج في `config/config.py`

```python
DEFAULT_TESSERACT = r'E:\renamer\Tesseract-OCR\tesseract.exe'
DEFAULT_POPPLER   = r'E:\renamer\poppler-25.12.0\Library\bin'
```

> أو اتركهم كما هم واضبطهم من داخل الـ app مباشرة.

### 2. شغّل البرنامج

```bash
python main.py
```

---

## طريقة الاستخدام

1. اضغط **"…"** جنب "مجلد الـ PDF" واختار الفولدر
2. تأكد إن مسار Tesseract و Poppler صح
3. اضبط الـ **DPI** (افتراضي 150، ارفعه لـ 200 لو الـ OCR بيغلط)
4. شغّل مع **Dry Run محفوظ** الأول عشان تشوف الأسماء قبل التغيير
5. لو الأسماء صح، **شيل علامة Dry Run** واضغط ابدأ تاني

---

## منطق التسمية

الـ Ref اللي بيتقرأ من الملف بيكون بالشكل ده:

```
1230 / QS / CONCORD / EHAF / GEN / 26 / 373 / REV00
  0     1      2       3     4    5    6     7
```

الاسم الجديد بيتكوّن من:

```
parts[1] + parts[4] + parts[6] + parts[7]
  QS    +   GEN    +   373    +  REV00
→  QS GEN 373 REV00.pdf
```

### تصحيح الـ OCR

Tesseract أحياناً بيقرأ الصفر `0` كحرف `O` في أرقام REV، البرنامج بيصلح ده تلقائياً:

```
REVOO  →  REV00  ✅
REVO1  →  REV01  ✅
```

---

## إعدادات متقدمة

| الإعداد | الوصف |
|---------|-------|
| **DPI** | دقة تحويل الـ PDF لصورة — ارفعه لو الـ OCR بيغلط، اخفضه لو البرنامج بطيء |
| **Dry Run** | معاينة الأسماء بدون تغيير فعلي |
| **Tesseract path** | مسار ملف `tesseract.exe` |
| **Poppler path** | مسار مجلد `bin` داخل Poppler |

---

## استكشاف الأخطاء

**مش لاقي Ref في الملف**
- ارفع الـ DPI لـ 200 أو 300
- تأكد إن الـ PDF مش corrupted أو محمي بكلمة سر

**popup window بتظهر وتختفي مع كل ملف**
- ده بيحصل لو `main.py` مش بيتشغّل صح — تأكد إن الكود الخاص بإخفاء الـ subprocess موجود في أول الملف

**خطأ `tesseract is not installed`**
- تأكد من مسار Tesseract في الإعدادات
- تأكد إن `tesseract.exe` موجود فعلاً في المسار ده

**خطأ في Poppler**
- تأكد إن المسار بيشير لمجلد `bin` مش مجلد `poppler` نفسه
