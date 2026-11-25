"""Rebuild the 'اضغط ابدأ' title prompt with correct sequential Enigma mapping."""
from __future__ import annotations
import importlib.util
import pathlib
import shutil
import subprocess
import sys

PROJ = pathlib.Path(r"C:\Users\reva4\Documents\Default Project\Phantasy Star IV")
sys.path.insert(0, str(PROJ / "scripts"))
from arabic_engine import encode_text  # noqa: E402


def load(name):
    fp = str(PROJ / "scripts" / name)
    spec = importlib.util.spec_from_file_location(name, fp)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


e = load('70_enigma.py')
c = load('74_enigma_compress.py')
FONT = (PROJ / "extract" / "font" / "arabic_font.bin").read_bytes()
GF = PROJ / "tools" / "ps4disasm" / "graphics" / "title"
PM = PROJ / "tools" / "ps4disasm" / "plane mappings" / "title"
NEO = PROJ / "tools" / "clownnemesis" / "nemesis.exe"
OUT = PROJ / "extract" / "graphics"

import arabic_reshaper
from bidi.algorithm import get_display

from title_glyphs_8x8 import GLYPHS, render_tile

text = "اضغط ابدأ"
visual = get_display(arabic_reshaper.reshape(text))
chars = [c for c in visual if c != ' ']
tile_for = {}
for ch in chars:
    assert ch in GLYPHS, f'missing glyph U+{ord(ch):04X}'
    if ch not in tile_for:
        tile_for[ch] = len(tile_for) + 1
print('glyph tiles:', len(tile_for), [f'U+{ord(c):04X}' for c in tile_for])

# 18-cell mapping, text centred in row 0
mapping = [0] * 18
start = (18 - len(visual)) // 2
for i, ch in enumerate(visual):
    mapping[start + i] = tile_for.get(ch, 0)
comp = c.enigma_compress(mapping)
back, _ = e.eni_decomp(comp)
assert back == mapping, 'mapping roundtrip failed'
print('mapping:', mapping)

# 11 original tiles; build glyph tiles at index 1..N, fg = white (index 1)
tiles = [bytes(32) for _ in range(11)]
for ch, idx in tile_for.items():
    tiles[idx] = render_tile(ch, 15, 0)

art_raw = OUT / 'press_start_fixed.raw'
art_comp = OUT / 'press_start_fixed.nemesis'
art_raw.write_bytes(b''.join(tiles))
subprocess.run([str(NEO), '-c', str(art_raw), str(art_comp)], check=True, capture_output=True)

art_path = GF / 'Intro Press Start Button text Nemesis.bin'
bak = art_path.with_suffix('.bin.english.bak')
if not bak.exists():
    shutil.copy2(art_path, bak)
shutil.copy2(art_comp, art_path)

map_path = PM / 'Press Start Button Enigma.bin'
mbak = map_path.with_suffix('.bin.english.bak')
if not mbak.exists():
    shutil.copy2(map_path, mbak)
map_path.write_bytes(comp)
print(f'installed art {art_path.stat().st_size}B, map {map_path.stat().st_size}B')
