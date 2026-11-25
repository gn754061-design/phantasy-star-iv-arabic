"""Rebuild title logo/subtitle using the proven 8x16 Arabic font, two tiles per glyph."""
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
FONT = (PROJ / 'extract' / 'font' / 'arabic_font.bin').read_bytes()
GF = PROJ / 'tools' / 'ps4disasm' / 'graphics' / 'title'
PM = PROJ / 'tools' / 'ps4disasm' / 'plane mappings' / 'title'
NEO = PROJ / 'tools' / 'clownnemesis' / 'nemesis.exe'


def build(text, art_name, map_name, width, height, row, fg, ntiles):
    raw, bad = encode_text(text)
    assert not bad, bad
    # distinct glyph bytes -> two tile indices each (top, bottom)
    tiles_for = {}
    for b in raw:
        if b == 0:
            continue
        if b not in tiles_for:
            tiles_for[b] = len(tiles_for) * 2 + 1
    print(f'{art_name}: {text!r} chars={len(raw)} glyphs={len(tiles_for)} ntiles={ntiles}')

    mapping = [0] * (width * height)
    start = max(0, (width - len(raw)) // 2)
    for i, b in enumerate(raw):
        if b == 0:
            continue
        col = start + i
        top, bottom = tiles_for[b], tiles_for[b] + 1
        mapping[row * width + col] = top
        if row + 1 < height:
            mapping[(row + 1) * width + col] = bottom

    comp = c.enigma_compress(mapping)
    back, _ = e.eni_decomp(comp)
    assert back == mapping, 'map roundtrip failed'

    art_path = GF / art_name
    tiles = [bytes(32) for _ in range(ntiles)]
    for b, top in tiles_for.items():
        glyph = FONT[b * 16:(b + 1) * 16]
        for half in (0, 1):
            tile = bytearray(32)
            for y in range(8):
                bits = glyph[half * 8 + y]
                for x in range(8):
                    if (bits >> (7 - x)) & 1:
                        tile[y*4 + x//2] |= fg << (4 if x % 2 == 0 else 0)
            tiles[top + half] = bytes(tile)

    rawp = PROJ / 'extract' / 'graphics' / (art_name + '.16px.raw')
    compp = PROJ / 'extract' / 'graphics' / (art_name + '.16px.nemesis')
    rawp.write_bytes(b''.join(tiles))
    subprocess.run([str(NEO), '-c', str(rawp), str(compp)], check=True, capture_output=True)
    shutil.copy2(compp, art_path)
    mappath = PM / map_name
    mbak = mappath.with_suffix('.bin.english.bak')
    if not mbak.exists():
        shutil.copy2(mappath, mbak)
    mappath.write_bytes(comp)
    print(f'  art={art_path.stat().st_size}B map={mappath.stat().st_size}B')


build('فانتاسي ستار', 'Phantasy Star Title Nemesis.bin',
      'Phantasy Star Title Enigma.bin', 17, 13, 5, 10, 130)
build('نهاية الألفية', 'The End of the Millennium Nemesis.bin',
      'The End of the Millennium Enigma.bin', 29, 3, 1, 3, 56)
