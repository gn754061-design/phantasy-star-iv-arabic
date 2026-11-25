import sys
sys.path.insert(0, 'scripts')
import arabic_reshaper
from bidi.algorithm import get_display
from prototype_arabic_font import GLYPHS

# 41 available slots:
# 26 slots: 57..82 (0x39..0x52)
# 15 slots: 88..102 (0x58..0x66)
available_bytes = list(range(57, 83)) + list(range(88, 103))
print(f"Available bytecode slots: {len(available_bytes)}")

# Map each of the 39 glyphs to a unique byte
glyph_list = sorted(list(GLYPHS.keys()))
CHAR_TO_WINDOW_BYTE = {}
WINDOW_BYTE_TO_CHAR = {}

for idx, ch in enumerate(glyph_list):
    b = available_bytes[idx]
    CHAR_TO_WINDOW_BYTE[ch] = b
    WINDOW_BYTE_TO_CHAR[b] = ch

def encode_menu_text(text: str) -> list[int]:
    reshaped = arabic_reshaper.reshape(text)
    visual = get_display(reshaped)
    out = []
    for ch in visual:
        if ch == ' ':
            out.append(0) # space = 0
        elif ch in CHAR_TO_WINDOW_BYTE:
            out.append(CHAR_TO_WINDOW_BYTE[ch])
        else:
            raise ValueError(f"Unmapped glyph U+{ord(ch):04X} in '{text}'")
    return out

# Test core menus
core_menus = {
    # Start menu
    "START": "ابدأ",
    "CONTINUE": "متابعة",
    "ERASE DATA": "حذف الحفظ",
    "NO DATA": "فارغ",
    # Action menu
    "ITEM": "أدوات",
    "TECH": "تقنية",
    "SKILL": "مهارة",
    "EQUIP": "عتاد",
    "STATE": "حالة",
    "TALK": "تحدث",
    "MACRO": "ماكرو",
    "MUMBL": "تمتمة",
}

for eng, ar in core_menus.items():
    enc = encode_menu_text(ar)
    hex_str = ", ".join(f"${b:02X}" for b in enc)
    print(f"{eng:12} -> {ar:10} -> {hex_str}")
