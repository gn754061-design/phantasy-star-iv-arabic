"""Inject 8x8 Arabic glyphs into Font Nemesis.bin."""

import subprocess
import sys
from pathlib import Path

PROJ = Path(r"C:\Users\reva4\Documents\Default Project\Phantasy Star IV")
sys.path.insert(0, str(PROJ / "scripts"))

from prototype_arabic_font import GLYPHS
from test_menu_encoding import CHAR_TO_WINDOW_BYTE
from menu_font_ext import NEW_GLYPH_ROWS, CHAR_TO_BYTE as EXTENDED_TO_BYTE

FONT_IN = PROJ / "extract" / "font" / "window_font_decompressed.bin"
FONT_OUT_BIN = PROJ / "extract" / "font" / "window_font_arabic_decompressed.bin"
NEMESIS_OUT = PROJ / "tools" / "ps4disasm" / "graphics" / "font" / "Font Nemesis.bin"
CLOWNNEMESIS = PROJ / "tools" / "clownnemesis" / "nemesis.exe"

data = bytearray(FONT_IN.read_bytes())
original_tile_count = len(data) // 32
print(f"Original tile count: {original_tile_count}")

# We need up to byte 101 ($65), which is tile index 100.
# Stopping at 101 tiles preserves WT[0x66] (VRAM $6E6, right/select arrow).
target_tile_count = 101
if len(data) < target_tile_count * 32:
    # Fill new tiles with solid blue (color 14 = 0xEE)
    needed = target_tile_count * 32 - len(data)
    data.extend(b"\xee" * needed)

print(f"Expanded to {len(data) // 32} tiles")

# Helper to pack 8x8 pixel rows into 32 bytes of 4bpp
def pack_tile(pixel_rows: list[str]) -> bytes:
    out = bytearray()
    for y in range(8):
        row_str = pixel_rows[y]
        for x in range(0, 8, 2):
            p0 = 15 if row_str[x] == '#' else 14
            p1 = 15 if row_str[x+1] == '#' else 14
            out.append((p0 << 4) | p1)
    return bytes(out)

# Inject each glyph
injected_count = 0
for ch, glyph_rows in GLYPHS.items():
    b = CHAR_TO_WINDOW_BYTE[ch]
    # LoadWindowTiles writes VRAM tile = $680 + byte value.  Title_ArtPtrs loads
    # ArtNem_WindowTiles at $680 and then ArtNem_Font at $681 (see ps4.asm), so
    # byte b actually displays art tile (b - 1).  Injecting at tile b shifted
    # every Arabic glyph one slot to the right and produced scrambled menus.
    tile_idx = b - 1
    tile_bytes = pack_tile(glyph_rows)
    data[tile_idx * 32 : (tile_idx + 1) * 32] = tile_bytes
    injected_count += 1

# Extra presentation forms used by the translated menu strings.
for slot, rows in NEW_GLYPH_ROWS.items():
    data[(slot - 1) * 32:slot * 32] = pack_tile(rows)
    injected_count += 1

print(f"Injected {injected_count} glyphs into decompressed font buffer.")

# Write decompressed bin
FONT_OUT_BIN.write_bytes(data)
print(f"Saved {FONT_OUT_BIN}")

# Compress with clownnemesis
cmd = [str(CLOWNNEMESIS), "-c", str(FONT_OUT_BIN), str(NEMESIS_OUT)]
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"ClownNemesis output: {res.stdout.strip()}")
if res.returncode != 0:
    print(f"ClownNemesis error: {res.stderr.strip()}")
    sys.exit(1)

print(f"Successfully compressed to {NEMESIS_OUT} (size: {NEMESIS_OUT.stat().st_size} bytes)")
