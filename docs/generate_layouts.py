"""Generate full, consistently positioned Glove80 SVGs from the keymap (stdlib only)."""
import argparse
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = ROOT / "docs/layouts"

# Physical rows in keyboard viewing order, including the two thumb rows.
# The short function and bottom finger rows have intentional empty columns.
ROWS = [
    [*range(5), *range(14, 19)],
    [*range(6), *range(13, 19)],
    [*range(6), *range(13, 19)],
    [*range(6), *range(13, 19)],
    [*range(9), *range(10, 19)],
    [*range(5), *range(6, 9), *range(10, 13), *range(14, 19)],
]

KEY_LABELS = {
    "LSHFT": "Shift", "LALT": "Alt", "RALT": "Dictation", "LCTRL": "Ctrl",
    "LGUI": "Cmd", "HYPER_MOD": "Hyper", "ESC": "Esc", "RET": "Enter",
    "SPACE": "Space", "TAB": "Tab", "DEL": "Del", "BSPC": "Bksp",
    "HOME": "Home", "END": "End", "PG_UP": "PgUp", "PG_DN": "PgDn",
    "LEFT": "←", "RIGHT": "→", "UP": "↑", "DOWN": "↓",
    "SQT": "'", "DQT": '"', "COMMA": ",", "DOT": ".", "FSLH": "/",
    "BSLH": "\\", "GRAVE": "`", "TILDE": "~", "CARET": "^", "AMPS": "&",
    "PIPE": "|", "AT": "@", "HASH": "#", "DLLR": "$", "MINUS": "−",
    "UNDER": "_", "LPAR": "(", "RPAR": ")", "LT": "<", "GT": ">",
    "LBKT": "[", "RBKT": "]", "LBRC": "{", "RBRC": "}",
    "COLON": ":", "SEMI": ";", "PRCNT": "%",
    "PLUS": "+", "ASTRK": "*", "EQUAL": "=", "C_MUTE": "Mute",
    "C_VOL_DN": "Vol−", "C_VOL_UP": "Vol+", "C_BRI_DN": "Bri−",
    "C_BRI_UP": "Bri+", "C_PREV": "Prev", "C_PP": "Play/Pause", "C_NEXT": "Next",
}
BEHAVIOR_LABELS = {
    "&none": "—", "&trans": "·", "&apo_dquote": "' / \"",
    "&comma_qmark": ", / ?", "&dot_excl": ". / !", "&slash_bslash": "/ / \\",
    "&ext_mod EXT MOD": "EXT/MOD", "&caps_word": "Caps Word",
    "&quick_swap": "QSWAP", "&swapper": "SWAP", "&tab_swapper": "TSWAP",
    "&tmx": "TMX", "&out OUT_USB": "OUT USB", "&out OUT_BLE": "OUT BLE",
    "&rgb_ug RGB_TOG": "RGB On/Off", "&rgb_ug RGB_HUI": "Hue+",
    "&rgb_ug RGB_HUD": "Hue−", "&rgb_ug RGB_BRI": "RGB Bri+",
    "&rgb_ug RGB_BRD": "RGB Bri−", "&rgb_ug RGB_EFF": "Effect+",
    "&rgb_ug RGB_EFR": "Effect−", "&rgb_ug RGB_SPI": "Speed+",
    "&rgb_ug RGB_SPD": "Speed−", "&rgb_ug RGB_STATUS": "Status",
    "&rgb_ug RGB_SAI": "Sat+", "&rgb_ug RGB_SAD": "Sat−",
    "&bt BT_CLR": "BT CLR", "&bt BT_PRV": "BT Prev", "&bt BT_NXT": "BT Next",
}


def key_label(code):
    if code in KEY_LABELS:
        return KEY_LABELS[code]
    if re.fullmatch(r"N[0-9]", code):
        return code[1:]
    if re.fullmatch(r"[A-Z]|F(?:[1-9]|1[0-2])", code):
        return code
    shortcut = re.fullmatch(r"(LG|LC|LS|LA)\((.*)\)", code)
    if shortcut:
        modifier = {"LG": "Cmd", "LC": "Ctrl", "LS": "Shift", "LA": "Alt"}[shortcut[1]]
        return f"{modifier}+{key_label(shortcut[2])}"
    raise ValueError(f"Unknown key code: {code}")


def binding_label(binding):
    if binding in BEHAVIOR_LABELS:
        return BEHAVIOR_LABELS[binding]
    behavior, *args = binding.split()
    if behavior == "&kp":
        return key_label(args[0])
    if behavior in ("&mo", "&sticky_layer"):
        return "Fn" if args[0] == "FN" else args[0]
    if behavior in ("&sk", "&hm"):
        return key_label(args[0]) + ("†" if behavior == "&sk" else "*")
    if behavior == "&bt" and args[0] == "BT_SEL":
        return f"BT {args[1]}"
    raise ValueError(f"Unknown binding: {binding}")


def render(name, bindings):
    assert len(bindings) == sum(map(len, ROWS)) == 80
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1640" height="426" '
        'viewBox="0 0 1640 426" role="img" aria-labelledby="title desc">',
        f'<title id="title">{name} layer</title>',
        '<desc id="desc">Full 80-key Glove80 layout in keyboard viewing order. '
        'All six finger rows and both thumb rows are shown, including disabled keys.</desc>',
        '<rect width="1640" height="426" rx="16" fill="#0f172a"/>',
        '<g font-family="system-ui, sans-serif" text-anchor="middle">',
        '<text x="272" y="32" fill="#94a3b8" font-size="14">LEFT</text>',
        '<text x="1364" y="32" fill="#94a3b8" font-size="14">RIGHT</text>',
    ]
    position = 0
    for row, columns in enumerate(ROWS):
        for column in columns:
            binding = bindings[position]
            label = binding_label(binding)
            x, y = 24 + 84 * column, 52 + 60 * row
            if binding == "&none":
                fill, stroke, color = "#131e31", "#28364b", "#64748b"
            elif binding == "&trans" or column in (*range(6, 9), *range(10, 13)):
                fill, stroke, color = "#153e48", "#4b9caa", "#a5f3fc"
            else:
                fill, stroke, color = "#243247", "#52647d", "#f1f5f9"
            size = 18 if len(label) <= 6 else 14 if len(label) <= 8 else 11
            lines.extend([
                f'<g data-position="{position}" data-binding="{escape(binding, quote=True)}">',
                f'<title>Position {position}: {escape(binding)}</title>',
                f'<rect x="{x}" y="{y}" width="76" height="50" rx="8" '
                f'fill="{fill}" stroke="{stroke}"/>',
                f'<text x="{x + 38}" y="{y + 30}" fill="{color}" '
                f'font-size="{size}">{escape(label)}</text>',
                '</g>',
            ])
            position += 1
    lines.append('</g></svg>')
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if diagrams are stale")
    args = parser.parse_args()
    text = (ROOT / "config/glove80.keymap").read_text()
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    stale = []
    expected_paths = set()
    for name, block in re.findall(r'label = "([A-Z]+)";\s*bindings = <(.*?)>;', text, re.S):
        bindings = [" ".join(b.split()) for b in re.findall(r"&\w+[^&]*", block)]
        path = LAYOUTS / f"{name.lower()}.svg"
        expected_paths.add(path)
        svg = render(name, bindings)
        if args.check:
            if not path.exists() or path.read_text() != svg:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(svg)
    obsolete = set(LAYOUTS.glob("*.svg")) - expected_paths
    if args.check:
        stale.extend(str(path.relative_to(ROOT)) for path in sorted(obsolete))
        if stale:
            parser.exit(1, "Stale diagrams: " + ", ".join(stale) + "\n")
    else:
        for path in obsolete:
            path.unlink()


if __name__ == "__main__":
    main()
