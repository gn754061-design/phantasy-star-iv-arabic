# سير العمل وإعادة البناء من الصفر

## المتطلبات
- Python: `C:\Users\reva4\.venvs\gt-venv\Scripts\python.exe`
  (المكتبات: `arabic-reshaper`, `python-bidi`, `Pillow`)
- المجمّع: `tools/ps4disasm/AS/win32/asw.exe` + `ps4p2bin.exe`
- أداة الباتش: `tools/flips/flips.exe`

## الخطوات
1. **لا تلمس** `original/`. كل البناء يبدأ من `tools/ps4disasm`.
2. بناء الخط العربي (إن لزم):
   ```
   python scripts/07_build_font.py
   ```
3. تثبيت الخط والرقعة الهندسية (مرة واحدة):
   ```
   python scripts/10_patch_engine.py
   python scripts/15_restore_english_font.py
   ```
   - `10` يرقّع `GetFontGraphics` إلى `andi.w #$FF,d1` ويوجه مؤشرين إلى `Art_DialogueFontArabic`.
   - `15` يستعيد الخط الإنجليزي الأصلي من الروم حتى لا تتحرك العناوين.
4. تحرير النص في `tools/ps4disasm/script/dialogue NN.asm`، ثم إعادة الضغط:
   ```
   python tools/ps4disasm/script/compress_script.py "tools/ps4disasm/script/dialogue NN.asm"
   ```
   - تأكد أن حجم `.bin` الجديد **يساوي** الحجم الأصلي (أضف/احذف حشواً في النهاية إن لزم)
     كي لا تتحرك بقية الكتل.
5. البناء:
   ```
   cd tools\ps4disasm
   cmd /c build.bat
   ```
   الناتج: `ps4built.bin` (يجب أن يظل 0x300000 بايت).
6. النسخ والباتش:
   ```
   copy ps4built.bin ..\..\work\ps4-arabic-canary.md
   flips --create original\*.md work\ps4-arabic-canary.md build\ps4-arabic-canary.bps
   flips --apply --exact build\ps4-arabic-canary.bps original\*.md build\_verify.md
   ```
   يجب أن يتطابق SHA-1 لـ `_verify.md` مع `ps4-arabic-canary.md`.

## أكواد التحكم المحظورة
`0xF2–0xFA`، `0xFC`، `0xFD`، `0xFE`، `0xFF` — لا تُترجم ولا تُعاد ترتيبها ولا تُحقن داخل الكلمات.
انظر `docs/CHARSETS.md` و`tools/ps4disasm/script/documentation.txt`.

## الترجمة على دفعات (Ollama)
```
python scripts/35_translate_ollama.py --start 0 --end 4953 --batch 70 \
  --model huihui_ai/qwen3.5-abliterated:9b \
  --out extract/text/script_ar_full_A.tsv
python scripts/35_translate_ollama.py --start 4953 --end 9905 --batch 60 \
  --model huihui_ai/qwen3.5-abliterated:9b \
  --out extract/text/script_ar_full_B.tsv
```
- النموذج `qwen3-vl:8b` غير مناسب: يستهلك >8000 رمز قبل الإخراج؛ استخدم `qwen3.5-abliterated:9b`.
- `think: false` إلزامي وإلا يعيد النموذج استجابة فارغة.
- السكربت تزايدي (resumable): يعيد تشغيله مع نفس `--out` يترجم الناقص فقط.
- الدمج: `python scripts/38_merge_translations.py`.

## الاختبار البصري داخل Sandbox (Docker)
صورة الحاوية: `ps4-sandbox:latest` (مبنية من `kilo-sandbox:latest` + BlastEm 1.0.0).
```
docker build -t ps4-sandbox:latest docker/
docker run --rm --entrypoint bash \
  -v "<rom>:/rom/game.md:ro" \
  -v "<build/sandbox>:/out" \
  -v "<docker>:/scripts:ro" \
  ps4-sandbox:latest /scripts/navigate3.sh
```
- `Xvfb :99` + `SDL_AUDIODRIVER=dummy` + `blastem -g` (تصيير برمجي).
- `xdotool windowfocus` ثم `keydown`/`keyup` مع ثبات 0.18s؛ الضغطات القصيرة جداً لا تصل للمحاكي.
- `import -window <id>` لالتقاط نافذة المحاكي، أو مفتاح `p` للقطة داخلية.
- اللقطات الحقيقية في `build/sandbox/`، أهمها `n3_04_after_a2.png`.

## حدود المساحة
- كتلة الحوار غير المضغوطة: ≤ 7887 بايت (القيمة العملية في الأصل ≤ 7220).
- إذا تجاوزت الترجمة الحد: قصّر النص، أو فعّل `dialogue_uncompressed = 1` في
  `ps4.options.asm` (يُنتج روماً أكبر)، أو انقل مخزن RAM إلى `0xFF2A90`.
