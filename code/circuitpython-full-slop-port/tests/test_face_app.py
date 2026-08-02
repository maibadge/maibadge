"""Host-side lifecycle tests for mixed static/GIF face media."""

import asyncio
import os
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

if "board" not in sys.modules:
    fake_board = types.SimpleNamespace()
    for pin_number in range(49):
        setattr(fake_board, "GPIO" + str(pin_number), pin_number)
    sys.modules["board"] = fake_board

fake_microcontroller = types.SimpleNamespace(nvm=bytearray(8))
sys.modules["microcontroller"] = fake_microcontroller

import config  # noqa: E402
from apps.face import FaceApp  # noqa: E402


class FakeDisplay:
    def __init__(self):
        self.calls = []
        self.fail_gif = False

    def stop_gif(self):
        self.calls.append(("stop", None))

    def start_gif(self, filename):
        self.calls.append(("start", filename))
        if self.fail_gif:
            raise ValueError("bad GIF")

    def update_gif(self, now):
        self.calls.append(("update", now))

    def show_image(self, filename):
        self.calls.append(("image", filename))

    def show_solid(self, color):
        self.calls.append(("solid", color))
        return []

    @staticmethod
    def label(text, x, y, color, scale=1):
        return (text, x, y, color, scale)


class FakeHardware:
    def __init__(self):
        self.display = FakeDisplay()

    def safe_outputs(self):
        pass


class FaceAppTests(unittest.TestCase):
    def setUp(self):
        self.original_media = config.FACE_MEDIA
        config.FACE_MEDIA = ("/static.jpg", "/animated.gif")
        fake_microcontroller.nvm[0] = 0

    def tearDown(self):
        config.FACE_MEDIA = self.original_media

    def test_static_and_gif_share_gallery_navigation(self):
        hardware = FakeHardware()
        app = FaceApp(hardware)
        asyncio.run(app.enter())
        self.assertIn(("image", "/static.jpg"), hardware.display.calls)

        app.handle_event(("press", "button", "A"), 1.0)
        self.assertTrue(app.gif_active)
        self.assertIn(("start", "/animated.gif"), hardware.display.calls)
        app.update(2.0)
        self.assertIn(("update", 2.0), hardware.display.calls)

        asyncio.run(app.exit())
        self.assertFalse(app.gif_active)
        self.assertEqual(hardware.display.calls[-1][0], "stop")

    def test_bad_gif_is_recoverable(self):
        hardware = FakeHardware()
        hardware.display.fail_gif = True
        app = FaceApp(hardware)
        app.index = 1
        asyncio.run(app.enter())
        self.assertFalse(app.gif_active)
        self.assertTrue(any(call[0] == "solid" for call in hardware.display.calls))
        self.assertEqual(app.handle_event(("press", "button", "B"), 3.0), "menu")


if __name__ == "__main__":
    unittest.main()
