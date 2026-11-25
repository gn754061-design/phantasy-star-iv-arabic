"""8x8 connected glyphs for title-screen Arabic (separate from menu font to avoid
changing menu byte assignments)."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prototype_arabic_font import GLYPHS as BASE

GLYPHS = dict(BASE)

# Extra presentation forms required by the title prompt (1px stroke, row-5 baseline).
EXTRA = {
    '\uFEB3': [  # initial Seen (سـ)
        "........", "........", "........", "..#.#.#.",
        "..#.#.#.", "#######.", "........", "........",
    ],
    '\uFEF2': [  # final Yaa (ـي)
        "........", "........", "........", "........",
        "..#..#..", ".#..####", "..###...", "..#.#...",
    ],
    '\uFEF3': [  # initial Yaa (يـ)
        "........", "........", "........", ".....#..",
        ".....#..", "######..", "........", "...#.#..",
    ],
    '\uFEE7': [  # initial Noon (نـ)
        "........", "....#...", "........", ".....#..",
        ".....#..", "######..", "........", "........",
    ],
    '\uFEF7': [  # isolated Laam-Alef with Hamza (لأ)
        "..##....", ".#......", "..##..#.", ".....#..",
        "..#..#..", ".#.##...", "..####..", "........",
    ],
    '\uFEC2': [  # final Taa (ـط)
        "....#...", "....#...", "....#...", "..####..",
        ".#...#..", ".#######", "........", "........",
    ],
    '\uFED0': [  # medial Ghain (ـغـ)
        "....#...", "........", "..####..", "...##...",
        "....#...", "########", "........", "........",
    ],
    '\uFEBF': [  # initial Dhaad (ضـ)
        "....#...", "........", "........", "..####..",
        ".#...#..", "#######.", "........", "........",
    ],
}
GLYPHS.update(EXTRA)


def render_tile(ch: str, fg: int = 15, bg: int = 0) -> bytes:
    rows = GLYPHS[ch]
    tile = bytearray(32)
    for y in range(8):
        for x in range(8):
            n = fg if rows[y][x] == '#' else bg
            tile[y*4 + x//2] |= n << (4 if x % 2 == 0 else 0)
    return bytes(tile)
