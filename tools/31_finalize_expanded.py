"""Pad the current uncompressed build to 4 MB, fix header/checksum, restore compressed build."""
from __future__ import annotations

import pathlib
import subprocess

PROJ = pathlib.Path(r"C:\Users\reva4\Documents\Default Project\Phantasy Star IV")
DIS = PROJ / "tools" / "ps4disasm"
OPT = DIS / "ps4.options.asm"
BAK = PROJ / "tools" / "ps4.options.compressed.bak2"


def checksum(d: bytes) -> int:
    t = 0
    for i in range(0x200, len(d) - 1, 2):
        t = (t + ((d[i] << 8) | d[i + 1])) & 0xFFFF
    return t


built = bytearray((DIS / "ps4built.bin").read_bytes())
assert len(built) <= 0x400000
built.extend(b"\xFF" * (0x400000 - len(built)))
built[0x1A4:0x1A8] = (0x003FFFFF).to_bytes(4, "big")
built[0x18E:0x190] = checksum(built).to_bytes(2, "big")
out = PROJ / "work" / "ps4-arabic-expanded.md"
out.write_bytes(built)
print(f"wrote {out.name}: 0x{len(built):X}, checksum {checksum(built):04X}")

# restore compressed option and rebuild the small canary ROM
if BAK.exists():
    OPT.write_bytes(BAK.read_bytes())
    subprocess.run(["cmd", "/c", "build.bat"], cwd=DIS, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (PROJ / "work" / "ps4-arabic-canary.md").write_bytes((DIS / "ps4built.bin").read_bytes())
    print("restored compressed canary build")
