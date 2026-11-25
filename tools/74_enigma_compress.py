"""Minimal Enigma compressor: emits code-7 runs of inline tile values.
Uses the same bitstream layout as the PSIV EniDecomp routine.
"""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib.util
_spec = importlib.util.spec_from_file_location('e', str(pathlib.Path(__file__).parent / '70_enigma.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)

INLINE_BITS = 7  # keeps every inline read inside the 9..16 bit window (no borrow path)


class BitWriter:
    def __init__(self):
        self.bits: list[int] = []

    def put(self, value: int, n: int) -> None:
        for i in range(n - 1, -1, -1):
            self.bits.append((value >> i) & 1)

    def bytes(self) -> bytes:
        bits = self.bits[:]
        while len(bits) % 8:
            bits.append(0)
        out = bytearray()
        for i in range(0, len(bits), 8):
            b = 0
            for bit in bits[i:i + 8]:
                b = (b << 1) | bit
            out.append(b)
        return bytes(out)


def enigma_compress(words: list[int], inline_bits: int = INLINE_BITS) -> bytes:
    bw = BitWriter()
    # emit in runs of up to 15 values (repeat nibble = count-1, 15 = terminator)
    i = 0
    while i < len(words):
        run = min(15, len(words) - i)
        bw.put(0x70 | (run - 1), 7)
        for w in words[i:i + run]:
            assert 0 <= w < (1 << inline_bits), w
            bw.put(w, inline_bits)
        i += run
    # terminator: code 7 with repeat 0xF
    bw.put(0x7F, 7)
    stream = bw.bytes()
    header = bytes([inline_bits, 0x00, 0x00, 0x00, 0x00, 0x00]) + stream[:2]
    return header + stream[2:]


if __name__ == '__main__':
    P = pathlib.Path(r'C:\Users\reva4\Documents\Default Project\Phantasy Star IV')
    src = (P / 'tools' / 'ps4disasm' / 'plane mappings' / 'title' /
           'Phantasy Star Title Enigma.bin').read_bytes()
    original, _ = e.eni_decomp(src)
    print('original words:', len(original))

    # round-trip test with a dummy mapping of the same length
    dummy = [(i % 70) for i in range(len(original))]
    comp = enigma_compress(dummy)
    back, used = e.eni_decomp(comp)
    print(f'roundtrip: {len(comp)} bytes, {len(back)} words, consumed {used}/{len(comp)}')
    print('match:', back == dummy)
    out = P / 'extract' / 'graphics' / 'enigma_roundtrip_test.bin'
    out.write_bytes(comp)
