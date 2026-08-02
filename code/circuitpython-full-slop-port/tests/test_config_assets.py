"""Host-side pin-map and asset-manifest checks."""

import os
import struct
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
        paths = list(config.FACE_MEDIA) + list(config.GIF_ASSETS) + [
            config.MENU_BACKGROUND,
            config.MENU_BACKGROUND_EMPTY,
            config.MENU_ITEM_SELECTED,
            config.MENU_ITEM_SMALL,
            config.SONG_BACKGROUND,
            config.SPLASH_IMAGE,
        ]
        for circuitpy_path in paths:
            host_path = os.path.join(ROOT, circuitpy_path.lstrip("/").replace("/", os.sep))
            self.assertTrue(os.path.isfile(host_path), host_path)

    def test_gifs_are_native_display_size(self):
        for circuitpy_path in config.GIF_ASSETS:
            host_path = os.path.join(ROOT, circuitpy_path.lstrip("/").replace("/", os.sep))
            with open(host_path, "rb") as gif_file:
                header = gif_file.read(10)
            self.assertIn(header[:6], (b"GIF87a", b"GIF89a"), host_path)
            self.assertEqual(struct.unpack("<HH", header[6:10]), (240, 240), host_path)

    def test_press_margin_exceeds_release_margin(self):
        self.assertGreater(config.TOUCH_PRESS_MARGIN, config.TOUCH_RELEASE_MARGIN)


if __name__ == "__main__":
    unittest.main()
