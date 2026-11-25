# مصادر الخطوط والترخيص

## خط الحوار العربي (`extract/font/arabic_font.bin`)
- **المصدر:** GNU Unifont 17.0.05 — `unifont-17.0.05.bdf`
  (الموقع: https://unifoundry.com/unifont)
- **الترخيص:**dual-license: SIL Open Font License 1.1 / GPL-2.0+ مع استثناء تضمين الخطوط.
- **السبب في الاختيار:** محارف Unifont العربية مقاس **8×16 بكسل بالضبط**،
  وهو نفس مقاس جليف خط الحوار في اللعبة (16 بايت/جليف، 1-bit لكل بكسل).
- **الملفات:**
  - `tools/unifont-17.0.05.bdf.gz` — التنزيل الأصلي.
  - `tools/unifont-17.0.05.bdf` — نسخة مفكوكة.
  - `scripts/07_build_font.py` — يبني الجليفات والخريطة والمعاينة.
  - `extract/font/arabic_font.bin` — 4096 بايت = 256 جليف × 16.
  - `extract/font/arabic_map.tbl` — ربط المحرف بالبايت.
  - `extract/font/font_preview.png` — معاينة كل الجليفات.

## تصميم دمج الخط (مهم)
الخط النهائي `extract/font/arabic_font.bin` يحتوي **الخط الإنجليزي الأصلي كاملاً**
في الجليفات `0x00–0x4F`، ثم المحارف العربية في `0x50–0xDF`.
السبب: `GetFontGraphics` تُستخدم أيضاً لشاشة العنوان/Nوافذ؛ إعادة توجيهها إلى خط عربي فقط
شوّهت شاشة العنوان. الدمج يجعل كل النصوص الإنجليزية الأصلية تُعرض كما كانت،
والعربية تستخدم الجليفات الجديدة. بُني بـ`scripts/19_build_combined_font.py`.

## خط اللعبة الأصلي
- `tools/ps4disasm/graphics/font/Dialogue Font.bin` — 1280 بايت = 80 جليف × 16.
- استُخرج من الروم الأصلي عند الإزاحة `0x2A3542` (انظر `scripts/15_restore_english_font.py`).
- **لم يُعدّل**؛ الخط العربي أُضيف في مساحة النهاية عند `0x2F4E14` مع إعادة توجيه مؤشرين فقط.

## مراجع أخرى للخطوط
- `retro-vault/font-vault` (GitHub) — خطوط بكسل مرخّصة للأنظمة 8/16-بت.
- `stgiga/UnifontEX` (GitHub) — نسخة موسّعة من Unifont.
- `ecklf/embedded-bitmap-fonts` (GitHub) — مجموعات BDF مدمجة.
- `tomchen/bdfparser` (GitHub) — مكتبة BDF بايثون (اختيارية).
- مثال تعريب عربي على نفس الجهاز: **Disney's Aladdin Arabic Localization**
  (https://romhackplaza.org/translations/disneys-aladdin-arabic-localization-arabic-translation-genesis)
