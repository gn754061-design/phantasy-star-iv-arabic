"""Python port of the PSIV 68k EniDecomp routine (ps4.asm ~line 85012)."""
from __future__ import annotations

MASKS = [(1 << n) - 1 for n in range(17)]


def _s8(b: int) -> int:
    return b - 256 if b & 0x80 else b


def _ror32(v: int, n: int) -> int:
    v &= 0xFFFFFFFF
    return ((v >> n) | (v << (32 - n))) & 0xFFFFFFFF


def _ror16(v: int, n: int) -> int:
    v &= 0xFFFF
    return ((v >> n) | (v << (16 - n))) & 0xFFFF


def _rol8(v: int, n: int) -> int:
    v &= 0xFF
    n %= 8
    return ((v << n) | (v >> (8 - n))) & 0xFF if n else v


def eni_decomp(data: bytes, start_tile: int = 0) -> tuple[list[int], int]:
    p = 0
    inline_bits = _s8(data[p]); p += 1
    v = _s8(data[p]); p += 1
    v &= 0xFFFFFFFF
    v = _ror32(v, 1)
    lo = _ror16(v & 0xFFFF, 1)
    d4 = (v & 0xFFFF0000) | lo
    flag_low = bool(d4 & 0x8000)     # tested after first swap
    flag_high = bool(d4 & 0x80000000)  # tested after second swap

    inc_word = (int.from_bytes(data[p:p+2], 'big') + start_tile) & 0xFFFF; p += 2
    lit_word = (int.from_bytes(data[p:p+2], 'big') + start_tile) & 0xFFFF; p += 2
    d5 = (data[p] << 8) | data[p+1]; p += 2
    d6 = 16
    out: list[int] = []

    def fetch_byte(length: int) -> None:
        nonlocal d6, d5, p
        d6 -= length
        if d6 < 9:
            d6 += 8
            d5 = ((d5 << 8) | (data[p] if p < len(data) else 0)) & 0xFFFF
            p += 1

    def fetch_inline() -> int:
        nonlocal d6, d5, p
        d3 = start_tile
        if flag_low:
            d6 -= 1
            if (d5 >> d6) & 1:
                d3 |= 0x1000
        if flag_high:
            d6 -= 1
            if (d5 >> d6) & 1:
                d3 |= 0x0800
        d1 = d5
        d7 = d6 - inline_bits
        if d7 < 0:
            d6 = (d7 + 16) & 0xFFFF
            shift = -d7
            d1 = (d1 << shift) & 0xFFFF
            d5 = (_rol8(data[p], shift) & MASKS[shift]) & 0xFF
            d1 = (d1 + d5) & 0xFFFF
        elif d7 == 0:
            d6 = 16
        else:
            d1 = (d1 >> d7) & 0xFFFF
        d1 = (d1 & MASKS[inline_bits]) + d3
        if d7 <= 0:
            # loc_41B92: fetch the next 16-bit word
            d5 = (data[p] << 8) | data[p+1]; p += 2
        else:
            # EniDecomp_FetchByte with d0 = inline_bits
            fetch_byte(inline_bits)
        return d1 & 0xFFFF

    while True:
        d0 = 7
        d7 = d6 - 7
        d1 = (d5 >> d7) & 0x7F
        d2 = d1
        if d1 < 0x40:
            d0 = 6
            d2 >>= 1
        fetch_byte(d0)
        repeat = d2 & 0xF
        code = (d1 >> 4)
        if code in (0, 1):
            w = inc_word
            for _ in range(repeat + 1):
                out.append(w); w = (w + 1) & 0xFFFF
        elif code in (2, 3):
            for _ in range(repeat + 1):
                out.append(lit_word)
        elif code == 4:
            w = fetch_inline()
            for _ in range(repeat + 1):
                out.append(w)
        elif code == 5:
            w = fetch_inline()
            for _ in range(repeat + 1):
                out.append(w); w = (w + 1) & 0xFFFF
        elif code == 6:
            w = fetch_inline()
            for _ in range(repeat + 1):
                out.append(w); w = (w - 1) & 0xFFFF
        elif code == 7:
            if repeat == 0xF:
                break
            for _ in range(repeat + 1):
                out.append(fetch_inline())
        if len(out) > 100000:
            raise RuntimeError('decompressor runaway')
    return out, p


if __name__ == '__main__':
    from pathlib import Path
    P = Path(r'C:\Users\reva4\Documents\Default Project\Phantasy Star IV')
    for name in ('Press Start Button Enigma.bin', 'Phantasy Star Title Enigma.bin'):
        d = (P / 'tools' / 'ps4disasm' / 'plane mappings' / 'title' / name).read_bytes()
        words, used = eni_decomp(d)
        print(f'\n{name}: {len(words)} words, consumed {used}/{len(d)} bytes')
        print('  first 40:', [f'{w:04X}' for w in words[:40]])
        tiles = [w & 0x7FF for w in words]
        print('  tile range:', min(tiles), max(tiles), 'distinct:', len(set(tiles)))
