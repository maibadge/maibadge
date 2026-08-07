"""Host-side retained-layout tests for the song playback screen."""

import asyncio
import os
import sys
import time
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

if "board" not in sys.modules:
    fake_board = types.SimpleNamespace()
    for pin_number in range(49):
        setattr(fake_board, "GPIO" + str(pin_number), pin_number)
    sys.modules["board"] = fake_board


class FakeBitmap:
    def __init__(self, width, height, value_count):
        del value_count
        self.width = width
        self.height = height
        self.pixels = [0] * (width * height)

    def fill(self, value):
        self.pixels = [value] * len(self.pixels)

    def __setitem__(self, position, value):
        x, y = position
        self.pixels[(y * self.width) + x] = value


class FakePalette:
    def __init__(self, size):
        self.colors = [0] * size
        self.transparent = set()

    def __setitem__(self, index, color):
        self.colors[index] = color

    def make_transparent(self, index):
        self.transparent.add(index)


class FakeTileGrid:
    def __init__(self, bitmap, pixel_shader, x=0, y=0):
        self.bitmap = bitmap
        self.pixel_shader = pixel_shader
        self.x = x
        self.y = y
        self.hidden = False


fake_displayio = sys.modules.setdefault("displayio", types.SimpleNamespace())
fake_displayio.Bitmap = FakeBitmap
fake_displayio.Palette = FakePalette
fake_displayio.TileGrid = FakeTileGrid

import config  # noqa: E402
from apps.song_app import SongApp  # noqa: E402


class FakeBuzzer:
    def tone(self, frequency):
        del frequency

    def off(self):
        pass


class FakeDisplay:
    def __init__(self):
        self.image_paths = []
        self.text_calls = []
        self.set_group_calls = 0
        self.group = None

    def image_group(self, filename):
        self.image_paths.append(filename)
        return [], []

    @staticmethod
    def rectangle(width, height, color, x=0, y=0):
        bitmap = FakeBitmap(width, height, 1)
        palette = FakePalette(1)
        palette[0] = color
        return FakeTileGrid(bitmap, palette, x, y)

    def pixel_text(self, text, x, y, color, background=0, transparent=False):
        self.text_calls.append((text, x, y, color, background, transparent))
        bitmap = FakeBitmap(max(1, len(text) * 8), 16, 2)
        palette = FakePalette(2)
        tile = FakeTileGrid(bitmap, palette, x, y)
        return tile, [bitmap, palette, tile]

    def set_group(self, group, resources=None):
        del resources
        self.group = group
        self.set_group_calls += 1


class FakeHardware:
    def __init__(self):
        self.buzzer = FakeBuzzer()
        self.display = FakeDisplay()

    def safe_outputs(self):
        pass


class SongAppTests(unittest.TestCase):
    def test_playback_screen_is_retained_and_uses_transparent_text(self):
        hardware = FakeHardware()
        app = SongApp(hardware, "song_intro")
        asyncio.run(app.enter())

        self.assertEqual(hardware.display.image_paths, [config.SONG_BACKGROUND])
        self.assertEqual(hardware.display.set_group_calls, 1)
        self.assertTrue(all(call[-1] for call in hardware.display.text_calls))
        self.assertIn("MAI INTRO", [call[0] for call in hardware.display.text_calls])

        app.update(time.monotonic() + 0.25)
        app.handle_event(("press", "button", "A"), time.monotonic())
        self.assertEqual(hardware.display.set_group_calls, 1)

    def test_playback_titles_fit_the_eighty_pixel_card(self):
        for title in SongApp.DISPLAY_TITLES.values():
            self.assertLessEqual(len(title) * 8, 80)

    def test_menu_controls_preserve_original_aliases(self):
        app = SongApp(FakeHardware(), "song_mario")
        self.assertEqual(app.handle_event(("press", "button", "B"), 1.0), "menu")
        self.assertEqual(app.handle_event(("press", "touch", "L4"), 1.0), "menu")


if __name__ == "__main__":
    unittest.main()
