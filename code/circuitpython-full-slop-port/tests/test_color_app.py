"""Host-side tests for the full-screen red/blue colour app."""

import asyncio
import os
import sys
import types
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

fake_board = sys.modules.setdefault("board", types.SimpleNamespace())
for pin_number in range(49):
    setattr(fake_board, "GPIO" + str(pin_number), pin_number)
fake_microcontroller = sys.modules.setdefault(
    "microcontroller", types.SimpleNamespace(nvm=bytearray(8))
)

import config  # noqa: E402
from apps.color import ColorApp, SCREEN_COLORS  # noqa: E402


class FakeDisplay:
    def __init__(self):
        self.colors = []

    def show_solid(self, color):
        self.colors.append(color)


class FakeHardware:
    def __init__(self):
        self.display = FakeDisplay()

    def safe_outputs(self):
        pass


class ColorAppTests(unittest.TestCase):
    def setUp(self):
        fake_microcontroller.nvm[3] = 255

    def test_reference_shades_and_bear_menu_order(self):
        self.assertEqual(SCREEN_COLORS, (0x52BDF4, 0xFF4101))
        self.assertEqual(config.MENU_ITEMS[1], ("color", "color"))

    def test_gallery_controls_cycle_and_open_menu(self):
        hardware = FakeHardware()
        app = ColorApp(hardware)
        asyncio.run(app.enter())
        self.assertEqual(hardware.display.colors[-1], 0x52BDF4)

        app.handle_event(("press", "button", "A"), 1.0)
        self.assertEqual(hardware.display.colors[-1], 0xFF4101)
        self.assertEqual(fake_microcontroller.nvm[3], 1)

        app.handle_event(("press", "touch", "L3"), 2.0)
        self.assertEqual(hardware.display.colors[-1], 0x52BDF4)
        self.assertEqual(app.handle_event(("press", "button", "B"), 3.0), "menu")


if __name__ == "__main__":
    unittest.main()
