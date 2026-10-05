"""Glove80 layout and behavior regression checks (stdlib only)."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
KEYMAP = ROOT / "config/glove80.keymap"
BASELINE = ROOT / "tests/fixtures/glove80.json"


def clean(text):
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)


def normalize(text):
    return " ".join(clean(text).split())


def layers(text):
    return {
        name: [normalize(binding) for binding in re.findall(r"&\w+[^&]*", bindings)]
        for name, bindings in re.findall(
            r'label = "([A-Z]+)";\s*bindings = <(.*?)>;', clean(text), re.S
        )
    }


class Glove80KeymapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keymap = KEYMAP.read_text()
        cls.layers = layers(cls.keymap)
        cls.baseline = json.loads(BASELINE.read_text())

    def test_all_layer_bindings_and_unused_keys(self):
        self.assertEqual(list(self.layers), ["BASE", "MOD", "EXT", "SYM", "NUM", "FN", "BT", "RGB"])
        self.assertEqual(list(self.layers), list(self.baseline["layers"]))
        for name, bindings in self.layers.items():
            with self.subTest(layer=name):
                self.assertEqual(len(bindings), 80)
                expected = ["&none"] * 80
                for position, binding in self.baseline["layers"][name].items():
                    expected[int(position)] = binding
                self.assertEqual(bindings, expected)

    def test_thumb_bindings(self):
        base = self.layers["BASE"]
        self.assertEqual(base[52:58], [
            "&sticky_layer SYM", "&none", "&mo RGB",
            "&mo BT", "&none", "&sticky_layer NUM",
        ])
        self.assertEqual(base[69:75], [
            "&ext_mod EXT MOD", "&kp BSPC", "&none",
            "&mo FN", "&kp RET", "&kp SPACE",
        ])
        self.assertEqual(self.layers["NUM"][52], "&trans")
        self.assertEqual(self.layers["NUM"][69], "&kp N0")
        for name, bindings in self.layers.items():
            with self.subTest(layer=name):
                for position in (53, 56, 71):
                    self.assertEqual(bindings[position], "&none")
                expected_rgb = {"BASE": "&mo RGB", "RGB": "&trans"}.get(name, "&none")
                expected_bt = {"BASE": "&mo BT", "BT": "&trans"}.get(name, "&none")
                self.assertEqual(bindings[54], expected_rgb)
                self.assertEqual(bindings[55], expected_bt)
                expected_fn = {"BASE": "&mo FN", "FN": "&trans"}.get(name, "&none")
                self.assertEqual(bindings[72], expected_fn)
        for name, trigger in (("BT", 55), ("RGB", 54)):
            for position in (*range(52, 58), *range(69, 75)):
                expected = "&trans" if position == trigger else "&none"
                if name == "BT" and position == 69:
                    expected = "&bt BT_SEL 0"
                self.assertEqual(self.layers[name][position], expected)

    def test_sym_num_triggers_on_home_row_and_displaced_keys_above(self):
        base = self.layers["BASE"]
        self.assertEqual(base[34], "&sticky_layer SYM")
        self.assertEqual(base[45], "&sticky_layer NUM")
        self.assertEqual(base.count("&sticky_layer SYM"), 2)
        self.assertEqual(base.count("&sticky_layer NUM"), 2)
        self.assertEqual(base[52], base[34])
        self.assertEqual(base[57], base[45])
        for name in ("MOD", "EXT", "SYM", "NUM", "FN"):
            self.assertEqual(self.layers[name][52], "&trans")
            self.assertEqual(self.layers[name][57], "&trans")
        self.assertEqual(base[22], "&kp ESC")
        self.assertEqual(base.count("&kp ESC"), 1)
        self.assertEqual(base[33], "&kp LS(RET)")
        self.assertEqual(self.layers["MOD"][22], "&kp ESC")
        self.assertEqual(self.layers["EXT"][22], "&kp LG(GRAVE)")
        for name in ("MOD", "EXT", "FN"):
            self.assertEqual(self.layers[name][34], "&trans")
            self.assertEqual(self.layers[name][45], "&trans")
        self.assertEqual(self.layers["SYM"][34], "&trans")
        self.assertEqual(self.layers["NUM"][45], "&trans")
        ns = {"svg": "http://www.w3.org/2000/svg"}
        svg = ET.parse(ROOT / "docs/layouts/base.svg").getroot()
        for above, trigger in ((22, 34), (33, 45)):
            top = svg.find(f'.//svg:g[@data-position="{above}"]/svg:rect', ns)
            bottom = svg.find(f'.//svg:g[@data-position="{trigger}"]/svg:rect', ns)
            self.assertEqual(top.get("x"), bottom.get("x"))
            self.assertEqual(int(top.get("y")) + 60, int(bottom.get("y")))

    def test_backspace_is_plain_and_delete_remains_on_ext(self):
        for name in ("BASE", "SYM", "NUM"):
            self.assertEqual(self.layers[name][70], "&kp BSPC")
        for name in ("MOD", "EXT", "FN"):
            self.assertEqual(self.layers[name][70], "&trans")
        self.assertNotIn("backspace_delete", self.keymap)
        self.assertEqual(self.layers["EXT"][60], "&kp DEL")

    def test_dictation_below_p_not_thumbs(self):
        base = self.layers["BASE"]
        self.assertEqual(base[16], "&none")
        self.assertEqual(base[59], "&kp P")
        self.assertEqual(base[75], "&kp RALT")
        ns = {"svg": "http://www.w3.org/2000/svg"}
        svg = ET.parse(ROOT / "docs/layouts/base.svg").getroot()
        p = svg.find('.//svg:g[@data-position="59"]/svg:rect', ns)
        dictation = svg.find('.//svg:g[@data-position="75"]', ns)
        rect = dictation.find("svg:rect", ns)
        self.assertEqual(rect.get("x"), p.get("x"))
        self.assertEqual(int(rect.get("y")), int(p.get("y")) + 60)
        self.assertEqual(dictation.find("svg:text", ns).text, "Dictation")
        self.assertEqual(base.count("&kp RALT"), 1)
        self.assertNotIn("&kp RALT", base[52:58] + base[69:75])
        self.assertEqual(self.layers["EXT"][28], "&none")
        self.assertNotIn("&kp RALT", self.layers["EXT"])

    def test_bluetooth_and_rgb_have_separate_hold_triggers(self):
        self.assertEqual(self.layers["BASE"][55], "&mo BT")
        self.assertEqual(self.layers["BASE"][54], "&mo RGB")
        self.assertNotIn("combo_bt", self.keymap)
        self.assertFalse(any(binding.startswith("&rgb_ug") for binding in self.layers["BT"]))
        self.assertFalse(any(binding.startswith(("&bt", "&out"))
                             for binding in self.layers["RGB"]))
        for number in range(5):
            position = self.layers["NUM"].index(f"&kp N{number}")
            binding = f"&bt BT_SEL {number}"
            self.assertEqual(self.layers["BT"][position], binding)
            self.assertEqual(self.layers["BT"].count(binding), 1)
        self.assertEqual(self.layers["BT"][49], "&none")
        self.assertEqual(self.layers["BT"][64], "&bt BT_CLR")
        self.assertEqual(self.layers["BT"][23], "&none")
        self.assertEqual(self.layers["BT"].count("&bt BT_CLR"), 1)
        self.assertEqual(self.layers["BT"][24:26], ["&out OUT_USB", "&out OUT_BLE"])

    def test_rgb_controls_have_vertical_increase_decrease_pairs(self):
        rgb = self.layers["RGB"]
        for position, increase, decrease in (
            (29, "HUI", "HUD"), (30, "SAI", "SAD"),
            (31, "BRI", "BRD"), (32, "SPI", "SPD"),
        ):
            self.assertEqual(rgb[position], f"&rgb_ug RGB_{increase}")
            self.assertEqual(rgb[position + 12], f"&rgb_ug RGB_{decrease}")
        self.assertEqual(rgb[28], "&rgb_ug RGB_TOG")
        self.assertEqual(rgb[40], "&rgb_ug RGB_STATUS")
        self.assertEqual(rgb[59:61], ["&rgb_ug RGB_EFR", "&rgb_ug RGB_EFF"])

    def test_base_media_controls_on_factory_function_keys(self):
        self.assertEqual(self.layers["BASE"][:10], [
            "&kp C_BRI_DN", "&kp C_BRI_UP", "&kp C_MUTE", "&kp C_VOL_DN",
            "&kp C_VOL_UP", "&kp C_PREV", "&kp C_PP", "&kp C_NEXT",
            "&none", "&none",
        ])
        self.assertNotIn("C_STOP", self.keymap)

    def test_alt_backspace_on_factory_right_arrow_and_left_is_empty(self):
        base = self.layers["BASE"]
        self.assertEqual(base[67:69], ["&none", "&kp LA(BSPC)"])
        self.assertEqual(base.count("&kp LA(BSPC)"), 1)
        self.assertEqual(base.count("&kp BSPC"), 1)
        self.assertEqual(self.layers["FN"][67:69], ["&kp F11", "&kp F12"])

    def test_enter_on_thumb_and_shift_enter_above_num(self):
        base = self.layers["BASE"]
        self.assertEqual(base[33], "&kp LS(RET)")
        self.assertEqual(base.count("&kp LS(RET)"), 1)
        self.assertEqual(base[73], "&kp RET")
        self.assertEqual(base.count("&kp RET"), 1)
        for name in ("EXT", "MOD"):
            self.assertEqual(self.layers[name][73], "&kp LS(RET)")
        self.assertEqual(self.layers["EXT"][45], "&trans")
        self.assertEqual(self.layers["MOD"][45], "&trans")
        self.assertEqual(self.layers["MOD"][33], "&trans")
        for name in ("SYM", "NUM", "FN"):
            self.assertEqual(self.layers[name][73], "&trans")
        self.assertEqual(self.layers["SYM"][45], "&kp LBRC")

    def test_navigation_moves_from_ext_to_base_factory_positions(self):
        for position, binding in {
            65: "&kp HOME", 66: "&kp END", 63: "&kp PG_UP", 79: "&kp PG_DN",
        }.items():
            with self.subTest(binding=binding):
                self.assertEqual(self.layers["BASE"][position], binding)
                self.assertNotIn(binding, self.layers["EXT"])
        for position in (29, 30, 32, 62):
            self.assertEqual(self.layers["EXT"][position], "&none")

    def test_num_decimal_and_equal_on_factory_left_side_arrows(self):
        num = self.layers["NUM"]
        self.assertEqual(num[67:69], ["&kp DOT", "&kp EQUAL"])
        self.assertEqual(num[52], "&trans")
        self.assertEqual(num[59], "&none")
        self.assertEqual(num.count("&kp DOT"), 1)
        self.assertEqual(num.count("&kp EQUAL"), 1)

    def test_num_underscore_stays_on_left_home_outer_key(self):
        num = self.layers["NUM"]
        position = 34
        self.assertEqual(num[position], "&kp UNDER")
        self.assertEqual(num[58], "&none")
        self.assertEqual(num.count("&kp UNDER"), 1)
        right_fingers = [*range(28, 34), *range(40, 46), *range(58, 64), *range(75, 80)]
        self.assertNotIn("&kp DOT", [num[position] for position in right_fingers])
        self.assertEqual(num[60], "&kp COMMA")

    def test_sym_braces_are_direct_keys_aligned_with_other_pairs(self):
        sym = self.layers["SYM"]
        self.assertEqual(sym[45], "&kp LBRC")  # Factory apostrophe
        self.assertEqual(sym[63], "&kp RBRC")  # Factory Page Up
        self.assertNotIn("combo_sym_lbrc", self.keymap)
        self.assertNotIn("combo_sym_rbrc", self.keymap)
        for opening, closing, position in (
            ("LPAR", "RPAR", 41), ("LT", "GT", 42),
            ("LBKT", "RBKT", 43), ("LBRC", "RBRC", 45),
        ):
            self.assertEqual(sym[position], f"&kp {opening}")
            self.assertEqual(sym[position + 18], f"&kp {closing}")

    def test_fn_matches_number_positions_and_extra_bottom_row(self):
        fn = self.layers["FN"]
        num = self.layers["NUM"]
        for number in range(1, 10):
            position = num.index(f"&kp N{number}")
            self.assertEqual(fn[position], f"&kp F{number}")
        self.assertEqual(fn[66:69], ["&kp F10", "&kp F11", "&kp F12"])
        self.assertEqual(
            sorted(binding for binding in fn if binding not in ("&none", "&trans")),
            sorted(f"&kp F{number}" for number in range(1, 13)),
        )
        self.assertNotIn("combo_mf_layer_thumbs", self.keymap)
        self.assertNotIn("&mo MF", self.keymap)

    def test_diagrams_are_current_and_show_the_same_full_layout(self):
        subprocess.run(
            [sys.executable, str(ROOT / "docs/generate_layouts.py"), "--check"],
            check=True,
        )
        ns = {"svg": "http://www.w3.org/2000/svg"}
        expected_geometry = None
        for name, bindings in self.layers.items():
            with self.subTest(layer=name):
                svg = ET.parse(ROOT / "docs/layouts" / f"{name.lower()}.svg").getroot()
                keys = svg.findall('.//svg:g[@data-position]', ns)
                self.assertEqual(len(keys), 80)
                self.assertEqual([key.get("data-position") for key in keys],
                                 [str(position) for position in range(80)])
                self.assertEqual([key.get("data-binding") for key in keys], bindings)
                geometry = [
                    tuple(key.find("svg:rect", ns).get(attribute)
                          for attribute in ("x", "y", "width", "height"))
                    for key in keys
                ]
                if expected_geometry is None:
                    expected_geometry = geometry
                self.assertEqual(geometry, expected_geometry)
                self.assertEqual(svg.get("viewBox"), "0 0 1640 426")

    def test_documented_layers_exist(self):
        readme = (ROOT / "README.md").read_text()
        images = re.findall(r"!\[.*?\]\((docs/layouts/[^)]+)\)", readme)
        self.assertEqual(len(images), len(self.layers))
        for image in images:
            title = ET.parse(ROOT / image).find("{http://www.w3.org/2000/svg}title").text
            self.assertIn(title.removesuffix(" layer"), self.layers)
        self.assertNotIn("SYM + NUM", readme)

    def test_behaviors_macros_combos_and_timing(self):
        # The full pre-keymap definition covers hold-tap settings, sticky flags,
        # macros, morphs, combo positions/layers, and timeouts.
        definitions = normalize(self.keymap.split("    keymap {")[0])
        self.assertEqual(definitions, self.baseline["definitions"])

    def test_swappers_ignore_the_left_home_shift(self):
        ignored = re.findall(r"ignored-key-positions = <(.*?)>;", self.keymap)
        self.assertEqual(ignored, ["35", "35"])
        self.assertEqual(self.layers["EXT"][35], "&sk LSHFT")

    def test_glove80_hardware_configuration(self):
        self.assertNotIn("sensor-bindings", self.keymap)
        self.assertIn("zmk,physical-layout = &physical_layout0;", self.keymap)


if __name__ == "__main__":
    unittest.main(verbosity=2)
