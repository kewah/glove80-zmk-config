"""Regression checks against the frozen Corne keymap (stdlib only)."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORNE = ROOT / "reference/corne_choc_pro.keymap"
GLOVE80 = ROOT / "config/glove80.keymap"

# Glove80's row-major matrix includes both thumb rows between finger columns.
# Thumb values are deliberately not a sequential copy of the Corne thumb row.
POSITIONS = {
    **dict(zip(range(0, 6), range(22, 28))),
    **dict(zip(range(8, 14), range(28, 34))),
    **dict(zip(range(14, 20), range(34, 40))),
    **dict(zip(range(22, 28), range(40, 46))),
    **dict(zip(range(28, 34), range(46, 52))),
    **dict(zip(range(34, 40), range(58, 64))),
    40: 54, 41: 71, 42: 70, 43: 73, 44: 72, 45: 55,
}


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


class CornePortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CORNE.read_text()
        cls.target = GLOVE80.read_text()
        cls.old_layers = layers(cls.source)
        cls.new_layers = layers(cls.target)

    def test_all_layer_bindings_and_unused_keys(self):
        self.assertEqual(list(self.old_layers), ["BASE", "MOD", "EXT", "SYM", "NUM", "MF", "BT"])
        self.assertEqual(list(self.new_layers), list(self.old_layers))
        for name, original in self.old_layers.items():
            with self.subTest(layer=name):
                self.assertEqual(len(original), 46)
                self.assertEqual(len(self.new_layers[name]), 80)
                expected = ["&none"] * 80
                for old, new in POSITIONS.items():
                    expected[new] = original[old]
                self.assertEqual(self.new_layers[name], expected)

    def test_thumb_orientation(self):
        base = self.new_layers["BASE"]
        self.assertEqual(base[52:58], [
            "&none", "&none", "&sticky_layer SYM",
            "&sticky_layer NUM", "&none", "&none",
        ])
        self.assertEqual(base[69:75], [
            "&none", "&backspace_delete", "&ext_mod EXT MOD",
            "&kp SPACE", "&kp RET", "&none",
        ])
        self.assertEqual(self.new_layers["NUM"][54], "&kp DOT")
        self.assertEqual(self.new_layers["NUM"][71], "&kp N0")

    def test_behaviors_macros_combos_and_timing(self):
        original = self.source.split("    keymap {")[0]
        expected = original.replace("&default_layout", "&physical_layout0")
        expected = expected.replace("ignored-key-positions = <15>;", "ignored-key-positions = <35>;")
        expected = re.sub(
            r"(?<![\w-])key-positions = <([\d ]+)>;",
            lambda m: "key-positions = <" + " ".join(
                str(POSITIONS[int(p)]) for p in m[1].split()
            ) + ">;",
            expected,
        )
        # Comparing the entire pre-keymap definition catches timing/flavor,
        # retro-tap, sticky flags, macros, morphs, combo layers and timeouts.
        self.assertEqual(normalize(self.target.split("    keymap {")[0]), normalize(expected))

    def test_swappers_ignore_the_left_home_shift(self):
        ignored = re.findall(r"ignored-key-positions = <(.*?)>;", self.target)
        self.assertEqual(ignored, ["35", "35"])
        self.assertEqual(self.new_layers["EXT"][35], "&sk LSHFT")

    def test_no_corne_hardware_references(self):
        self.assertNotIn("sensor-bindings", self.target)
        self.assertNotIn("&default_layout", self.target)


if __name__ == "__main__":
    unittest.main(verbosity=2)
