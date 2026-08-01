"""Host-side pin-map and asset-manifest checks."""

import os
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fake_board = types.SimpleNamespace()
for pin_number in range(49):
    setattr(fake_board, "GPIO" + str(pin_number), pin_number)
sys.modules.setdefault("board", fake_board)
sys.path.insert(0, ROOT)

import config  # noqa: E402


class ConfigTests(unittest.TestCase):
    def test_touch_gpio_map_is_complete_and_unique(self):
        names = [name for name, _ in config.TOUCH_CONFIG]
        pins = [pin for _, pin in config.TOUCH_CONFIG]
        self.assertEqual(set(names), {"L1", "L2", "L3", "L4", "R1", "R2", "R3", "R4"})
        self.assertEqual(set(pins), set(range(1, 9)))

    def test_all_manifest_assets_exist(self):
        paths = list(config.FACE_IMAGES) + [
            config.MENU_BACKGROUND,
            config.MENU_BACKGROUND_EMPTY,
            config.MENU_ITEM_SELECTED,
            config.MENU_ITEM_SMALL,
        ]
        for circuitpy_path in paths:
            host_path = os.path.join(ROOT, circuitpy_path.lstrip("/").replace("/", os.sep))
            self.assertTrue(os.path.isfile(host_path), host_path)

    def test_press_margin_exceeds_release_margin(self):
        self.assertGreater(config.TOUCH_PRESS_MARGIN, config.TOUCH_RELEASE_MARGIN)


if __name__ == "__main__":
    unittest.main()
