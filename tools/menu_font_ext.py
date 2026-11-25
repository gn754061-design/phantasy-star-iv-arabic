"""Extended 8x8 menu font: maps presentation forms used by Arabic menus & battle
onto safe byte slots ($09..$1A, $39..$52, $57..$65), leaving digits ($1B..$2E),
icons/punctuation ($2F..$38, $53..$56), and WT[0x66..$7F] untouched.

LoadWindowTiles and battle loc_27DB92 both write VRAM tile $680 + byte.
Title_ArtPtrs loads ArtNem_Font at $681, so byte b displays tile index b-1.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import arabic_reshaper
from bidi.algorithm import get_display

from prototype_arabic_font import GLYPHS
from test_menu_encoding import CHAR_TO_WINDOW_BYTE as BASE

PROJ = pathlib.Path(r"C:\Users\reva4\Documents\Default Project\Phantasy Star IV")

# Safe free slots:
# - $01..$08 ('A'..'H') preserved; $09..$1A ('I'..'Z', 18 slots) free
# - $1B..$24 ('0'..'9') and $25..$2E (small HP/TP '0'..'9') preserved!
# - $2F..$38 (UI/interrupt icons & '-!?:') preserved!
# - $39..$52 (26 slots) and $58..$64 (13 slots) used by BASE
# - $57 and $65 (2 slots) free; stop at $65 (101 tiles) so WT[$66] arrow is intact!
FREE_SLOTS = list(range(0x09, 0x1B)) + [0x57, 0x65]

ASCII_SLOT = {
    '!': 0x32, '?': 0x33, ':': 0x34, '.': 0x53,
    ',': 0x55, "'": 0x54, '-': 0x31, '_': 0x31,
    '\u061f': 0x33, '\u060c': 0x55,
}

# Hand-crafted 1px-stroke 8x8 glyphs locked to the y=5 baseline of prototype_arabic_font.
# Col 0 = left, col 7 = right. '#' = fg (15), '.' = bg (14).
HANDCRAFTED_GLYPHS: dict[str, list[str]] = {
    '\uFEB3': [  # ﺳ initial seen
        "........",
        "........",
        "........",
        "..#.#.#.",
        "..#.#.#.",
        "#######.",
        "........",
        "........",
    ],
    '\uFEF3': [  # ﻳ initial yaa
        "........",
        "........",
        "........",
        ".....#..",
        ".....#..",
        "######..",
        "........",
        "...#.#..",
    ],
    '\uFEE7': [  # ﻧ initial noon
        "........",
        "....#...",
        "........",
        ".....#..",
        ".....#..",
        "######..",
        "........",
        "........",
    ],
    '\uFEE0': [  # ﻠ medial lam
        "...#....",
        "...#....",
        "...#....",
        "...#....",
        "...#....",
        "########",
        "........",
        "........",
    ],
    '\uFED7': [  # ﻗ initial qaaf
        "........",
        "...#.#..",
        "........",
        "...###..",
        "...#.#..",
        "######..",
        "........",
        "........",
    ],
    '\uFEE6': [  # ﻦ final noon
        "........",
        "...#....",
        "........",
        "........",
        ".#....#.",
        ".#....##",
        ".#....#.",
        "..####..",
    ],
    '\uFEF2': [  # ﻲ final yaa
        "........",
        "........",
        "........",
        "........",
        "....####",
        ".#....#.",
        "..####..",
        "...#.#..",
    ],
    '\uFE92': [  # ﺒ medial baa
        "........",
        "........",
        "........",
        "...#....",
        "...#....",
        "########",
        "........",
        "...#....",
    ],
    '\uFEB4': [  # ﺴ medial seen
        "........",
        "........",
        "........",
        "..#.#.#.",
        "..#.#.#.",
        "########",
        "........",
        "........",
    ],
    '\uFEDC': [  # ﻜ medial kaaf
        "....###.",
        "...#....",
        "..#.....",
        "...#....",
        "....#...",
        "########",
        "........",
        "........",
    ],
    '\uFEDE': [  # ﻞ final lam
        ".....#..",
        ".....#..",
        ".....#..",
        ".....#..",
        ".....#..",
        ".#...###",
        ".#...#..",
        "..###...",
    ],
    '\uFEBC': [  # ﺼ medial saad
        "........",
        "........",
        "........",
        "..####..",
        ".#...#..",
        "########",
        "........",
        "........",
    ],
    '\uFE9F': [  # ﺟ initial jeem
        "........",
        "........",
        "........",
        "..###...",
        ".....#..",
        "######..",
        "........",
        "...#....",
    ],
    '\uFEB7': [  # ﺷ initial sheen
        "....#...",
        "...#.#..",
        "........",
        "..#.#.#.",
        "..#.#.#.",
        "#######.",
        "........",
        "........",
    ],
    '\uFEFC': [  # ﻼ final lam-alef
        ".#...#..",
        ".#...#..",
        "..#..#..",
        "...#.#..",
        "....##..",
        "..######",
        "........",
        "........",
    ],
    '\uFEE5': [  # ﻥ isolated noon
        "........",
        "...#....",
        "........",
        "........",
        ".#....#.",
        ".#....#.",
        ".#....#.",
        "..####..",
    ],
    '\uFE80': [  # ﺀ isolated hamza
        "........",
        "........",
        "...##...",
        "..#.....",
        "..####..",
        "........",
        "........",
        "........",
    ],
    '\uFEB0': [  # ﺰ final zay
        "........",
        "........",
        "....#...",
        "........",
        "........",
        "....####",
        "..##....",
        ".#......",
    ],
    '\uFEC4': [  # ﻄ medial taa
        "..#.....",
        "..#.....",
        "..#.....",
        "..####..",
        "..#...#.",
        "########",
        "........",
        "........",
    ],
    '\uFEBB': [  # ﺻ initial saad
        "........",
        "........",
        "........",
        "..####..",
        ".#...#..",
        "######..",
        "........",
        "........",
    ],
}

# Strict per-letter fallbacks (never map across unrelated letters).
FAMILY = [
    (0xFE80, 0xFE81, '\uFE83'),  # hamza / madda
    (0xFE82, 0xFE84, '\uFE83'),  # alef hamza/madda above
    (0xFE85, 0xFE86, '\uFEED'),  # waw hamza
    (0xFE87, 0xFE88, '\uFE8D'),  # alef hamza below -> isolated alef
    (0xFE89, 0xFE8C, '\uFEF4'),  # yaa hamza -> medial yaa
    (0xFE8D, 0xFE8E, '\uFE8D'),  # alef
    (0xFE8F, 0xFE92, '\uFE91'),  # baa
    (0xFE93, 0xFE94, '\uFE93'),  # taa marbuta
    (0xFE95, 0xFE98, '\uFE95'),  # taa
    (0xFE99, 0xFE9C, '\uFE99'),  # thaa
    (0xFE9D, 0xFEA0, '\uFEA0'),  # jeem
    (0xFEA1, 0xFEA4, '\uFEA3'),  # haa
    (0xFEA5, 0xFEA8, '\uFEA3'),  # khaa -> haa
    (0xFEA9, 0xFEAA, '\uFEA9'),  # dal
    (0xFEAB, 0xFEAC, '\uFEAC'),  # dhal (keep dot)
    (0xFEAD, 0xFEAE, '\uFEAD'),  # raa
    (0xFEAF, 0xFEB0, '\uFEB0'),  # zay (keep dot)
    (0xFEB1, 0xFEB4, '\uFEB3'),  # seen
    (0xFEB5, 0xFEB8, '\uFEB7'),  # sheen (keep 3 dots)
    (0xFEB9, 0xFEBC, '\uFEBB'),  # saad
    (0xFEBD, 0xFEC0, '\uFEBC'),  # daad -> saad shape (closer than zah)
    (0xFEC1, 0xFEC4, '\uFEC4'),  # taa (no zah dot!)
    (0xFEC5, 0xFEC8, '\uFEC6'),  # zah (with dot)
    (0xFEC9, 0xFECC, '\uFECB'),  # ain
    (0xFECD, 0xFED0, '\uFECD'),  # ghain
    (0xFED1, 0xFED4, '\uFED1'),  # faa
    (0xFED5, 0xFED8, '\uFED8'),  # qaaf (2 dots, never faa)
    (0xFED9, 0xFEDC, '\uFEDB'),  # kaaf (never qaaf!)
    (0xFEDD, 0xFEE0, '\uFEDF'),  # lam
    (0xFEE1, 0xFEE4, '\uFEE1'),  # meem
    (0xFEE5, 0xFEE8, '\uFEE8'),  # noon (never meem!)
    (0xFEE9, 0xFEEC, '\uFEEB'),  # haa (never meem!)
    (0xFEED, 0xFEEE, '\uFEED'),  # waw
    (0xFEEF, 0xFEF0, '\uFEF2'),  # alef maksura -> final yaa
    (0xFEF1, 0xFEF4, '\uFEF4'),  # yaa (never haa!)
    (0xFEF5, 0xFEFC, '\uFEFC'),  # lam-alef variants -> final lam-alef
]


def family_fallback(ch: str) -> str | None:
    cp = ord(ch)
    for lo, hi, rep in FAMILY:
        if lo <= cp <= hi and rep in CHAR_TO_BYTE:
            return rep
    return None


CHAR_TO_BYTE = dict(BASE)
CHAR_TO_BYTE.update(ASCII_SLOT)
NEW_GLYPH_ROWS: dict[int, list[str]] = {}
ALLOCATED: list[tuple[str, int]] = []

for _ch, _slot in zip(HANDCRAFTED_GLYPHS.keys(), FREE_SLOTS):
    CHAR_TO_BYTE[_ch] = _slot
    NEW_GLYPH_ROWS[_slot] = HANDCRAFTED_GLYPHS[_ch]
    ALLOCATED.append((_ch, _slot))


def encode_menu_text(text: str) -> tuple[bytes, list[str]]:
    """Visual-order byte string plus list of characters that could not be mapped."""
    visual = get_display(arabic_reshaper.reshape(text))
    out = bytearray()
    bad = []
    for ch in visual:
        if ch == ' ':
            out.append(0)
        elif ch == '\u0640':
            out.append(0x3B)  # tatweel -> baseline stroke
        elif 0x0660 <= ord(ch) <= 0x0669:
            out.append(0x1B + ord(ch) - 0x0660)
        elif '0' <= ch <= '9':
            out.append(0x1B + ord(ch) - ord('0'))
        elif ch in CHAR_TO_BYTE:
            out.append(CHAR_TO_BYTE[ch])
        elif 0xFE70 <= ord(ch) < 0xFF00:
            rep = family_fallback(ch)
            if rep and rep in CHAR_TO_BYTE:
                out.append(CHAR_TO_BYTE[rep])
            else:
                bad.append(ch)
                out.append(0)
        else:
            bad.append(ch)
            out.append(0)
    return bytes(out), bad


if __name__ == '__main__':
    print(f'base {len(BASE)} glyphs, {len(ALLOCATED)} new slots, '
          f'{len(CHAR_TO_BYTE)} total mapped chars')
    print('new slots:', ' '.join(f'U+{ord(c):04X}->${b:02X}' for c, b in ALLOCATED))
