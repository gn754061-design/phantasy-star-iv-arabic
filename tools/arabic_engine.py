"""Arabic encoding engine for Phantasy Star IV.

Pipeline: UTF-8 Arabic text -> arabic-reshaper -> python-bidi (visual order)
-> byte values from extract/font/arabic_map.tbl -> PSIV script bytes.

Control codes are never passed through the reshaper.
"""
from __future__ import annotations

import pathlib
import re

import arabic_reshaper
from bidi.algorithm import get_display

PROJ = pathlib.Path(r"C:\Users\reva4\Documents\Default Project\Phantasy Star IV")
MAP_FILE = PROJ / "extract" / "font" / "arabic_map.tbl"

_line_re = re.compile(r"^\s*dc\.b\s+\"(.*)\"\s*(;.*)?$")


def load_map(path: pathlib.Path = MAP_FILE) -> tuple[dict[str, int], dict[int, str]]:
    char_to_byte: dict[str, int] = {}
    byte_to_char: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        byte_hex, cp = line.split(":")
        codepoint = int(cp[2:], 16)
        char_to_byte[chr(codepoint)] = int(byte_hex, 16)
        byte_to_char[int(byte_hex, 16)] = chr(codepoint)
    return char_to_byte, byte_to_char


CHAR_TO_BYTE, BYTE_TO_CHAR = load_map()


def _is_ar_mapped(ch: str) -> bool:
    cp = ord(ch)
    return (0x0600 <= cp <= 0x06FF or 0xFE70 <= cp <= 0xFEFF or 0xFB50 <= cp <= 0xFDFF)


def encode_text(text: str) -> tuple[bytes, list[str]]:
    """Return encoded bytes and a list of unmapped characters.

    PSIV writes text tiles into VRAM left-to-right, one byte at a time.
    Arabic therefore has to be stored in *visual* order (the output of
    arabic-reshaper + python-bidi), exactly like the title/intro strings.
    A previous revision reversed the visual runs back to logical order,
    which made every line display mirrored. Do not reintroduce that reversal.
    """
    reshaped = arabic_reshaper.reshape(text)
    chars = list(get_display(reshaped))
    out = bytearray()
    unmapped: list[str] = []
    for ch in chars:
        if ch == " ":
            out.append(0x00)
        elif ch in CHAR_TO_BYTE:
            out.append(CHAR_TO_BYTE[ch])
        else:
            unmapped.append(ch)
            out.append(0x00)
    return bytes(out), unmapped


def decode_text(raw: bytes) -> str:
    """Reverse the byte mapping (for verification; no shaping reversal)."""
    return "".join(BYTE_TO_CHAR.get(b, "?") for b in raw)


def encode_asm_string(line: str) -> str:
    """Turn a `dc.b "text"` asm line into `dc.b $XX, $YY, ...`."""
    m = _line_re.match(line)
    if not m:
        raise ValueError(f"not a dc.b string line: {line!r}")
    text = m.group(1).replace('""', '"')
    raw, unmapped = encode_text(text)
    if unmapped:
        raise ValueError(f"unmapped characters in {text!r}: {sorted(set(unmapped))}")
    if len(raw) > 0x7F:
        raise ValueError("string too long for one byte-length context")
    return "\t\tdc.b\t" + ", ".join(f"${b:02X}" for b in raw) + "\n"


if __name__ == "__main__":
    sample = "مرحبا بك يا صائد النجوم، هل أنت مستعد لإنقاذ النظام الشمسي؟"
    raw, bad = encode_text(sample)
    print("input :", sample)
    print("bytes :", raw.hex(" "))
    print("length:", len(raw), "unmapped:", bad)
    print("decode:", decode_text(raw))
