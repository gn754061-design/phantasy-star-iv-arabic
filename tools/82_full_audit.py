"""Comprehensive audit of the final Arabic build."""
from __future__ import annotations
import importlib.util
import pathlib
import re
import subprocess
import sys

P = pathlib.Path(r'C:\Users\reva4\Documents\Default Project\Phantasy Star IV')
sys.path.insert(0, str(P / 'scripts'))


def load(name):
    fp = str(P / 'scripts' / name)
    spec = importlib.util.spec_from_file_location(name, fp)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


proto = load('prototype_arabic_font.py')
tenc = load('test_menu_encoding.py')
mext = load('menu_font_ext.py')

# 1. window font audit: every Arabic slot used in rev!=0 wincharset strings must match tile (b-1)
font = (P / 'extract' / 'font' / 'window_font_arabic_decompressed.bin').read_bytes()
used_bytes = set()
in_wc = False
in_rev0 = False
for line in (P / 'tools' / 'ps4disasm' / 'ps4.asm').read_text(encoding='latin-1').splitlines():
    s = line.strip()
    if s.startswith('if revision=0'):
        in_rev0 = True
    elif in_rev0 and s in ('else', 'endif'):
        in_rev0 = False
    if 'include' in s and 'wincharset.asm' in s:
        in_wc = True
    elif s == 'charset' or s.startswith('charset '):
        in_wc = False
    elif in_wc and not in_rev0 and 'dc.b' in s:
        for hx in re.findall(r'\$([0-9A-Fa-f]{2})', s):
            b = int(hx, 16)
            if (0x09 <= b <= 0x1A) or (0x39 <= b <= 0x52) or (0x57 <= b <= 0x65):
                used_bytes.add(b)

inv_base = {v: k for k, v in tenc.CHAR_TO_WINDOW_BYTE.items()}
bad = []
for b in sorted(used_bytes):
    if b in inv_base:
        expected = proto.GLYPHS[inv_base[b]]
    elif b in mext.NEW_GLYPH_ROWS:
        expected = mext.NEW_GLYPH_ROWS[b]
    else:
        continue
    tile = font[(b - 1) * 32 : b * 32]
    ok = True
    for y in range(8):
        for x in range(8):
            n = (tile[y * 4 + x // 2] >> (4 if x % 2 == 0 else 0)) & 15
            actual = '#' if n == 15 else '.'
            if actual != expected[y][x]:
                ok = False
    if not ok:
        bad.append(hex(b))
print(f'1) window-font bytes used: {len(used_bytes)}; font tiles: {len(font)//32}; mismatched glyph tiles: {len(bad)} {bad}')

# 2. translation validation
res = subprocess.run([sys.executable, str(P / 'scripts' / '37_validate_translation.py')],
                     capture_output=True, text=True, env={'PYTHONIOENCODING': 'utf-8', 'PATH': ''})
print('2) translation validator:\n', res.stdout.strip())

# 3. hanging prepositions
res = subprocess.run([sys.executable, str(P / 'scripts' / 'list_hanging.py')],
                     capture_output=True, text=True, env={'PYTHONIOENCODING': 'utf-8', 'PATH': ''})
print('3) hanging check:\n', res.stdout.strip()[-500:])

# 4. remaining obvious English UI strings in rev!=0 wincharset
in_wc = False
in_rev0 = False
hits = []
for i, line in enumerate((P / 'tools' / 'ps4disasm' / 'ps4.asm').read_text(encoding='latin-1').splitlines(), 1):
    s = line.strip()
    if s.startswith('if revision=0'):
        in_rev0 = True
    elif in_rev0 and s in ('else', 'endif'):
        in_rev0 = False
    if 'include' in s and 'wincharset.asm' in s:
        in_wc = True
    elif s == 'charset' or s.startswith('charset '):
        in_wc = False
    elif in_wc and not in_rev0 and 'dc.b' in s and '"' in s:
        if any(c.isalpha() for c in s.split('"', 1)[1]):
            hits.append((i, s))
print(f'4) remaining ASCII alpha wincharset strings: {len(hits)}')
for i, s in hits[:40]:
    print(f'   {i}: {s}')
