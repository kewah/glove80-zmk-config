"""Glove80 layout and behavior regression checks (stdlib only)."""
import json
from pathlib import Path
import re
import unittest

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
        self.assertEqual(list(self.layers), ["BASE", "MOD", "EXT", "SYM", "NUM", "MF", "BT"])
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
            "&sticky_layer SYM", "&none", "&none",
            "&none", "&none", "&sticky_layer NUM",
        ])
        self.assertEqual(base[69:75], [
            "&ext_mod EXT MOD", "&backspace_delete", "&none",
            "&none", "&kp RET", "&kp SPACE",
        ])
        self.assertEqual(self.layers["NUM"][52], "&kp DOT")
        self.assertEqual(self.layers["NUM"][69], "&kp N0")
        for name, bindings in self.layers.items():
            with self.subTest(layer=name):
                for position in (53, 54, 55, 56, 71, 72):
                    self.assertEqual(bindings[position], "&none")
        for position in (*range(52, 58), *range(69, 75)):
            self.assertEqual(self.layers["BT"][position], "&none")

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
