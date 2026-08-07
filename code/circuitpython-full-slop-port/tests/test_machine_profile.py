"""Host-side checks for the machine_v2 profile and two-button bindings."""

import os
import sys
import types
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

fake_board = sys.modules.setdefault("board", types.SimpleNamespace())
for pin_number in range(49):
    setattr(fake_board, "GPIO" + str(pin_number), pin_number)
sys.modules.setdefault("microcontroller", types.SimpleNamespace(nvm=bytearray(8)))

import config  # noqa: E402
from apps.face import FaceApp  # noqa: E402
from apps.menu import MenuApp  # noqa: E402
from apps.song_app import SongApp  # noqa: E402
from boards import machine_v2  # noqa: E402


class FakeLeds:
    def __init__(self):
        self.cycles = 0

    def next_color(self):
        self.cycles += 1


class FakeBuzzer:
    def tone(self, frequency):
        del frequency

    def off(self):
        pass


class FakeHardware:
    def __init__(self):
        self.leds = FakeLeds()
        self.buzzer = FakeBuzzer()


class MachineProfileTests(unittest.TestCase):
    def setUp(self):
        self.original_bindings = config.CONTROL_BINDINGS
        config.CONTROL_BINDINGS = machine_v2.CONTROL_BINDINGS
        self.hardware = FakeHardware()

    def tearDown(self):
        config.CONTROL_BINDINGS = self.original_bindings

    def test_machine_pin_map_and_capabilities(self):
        self.assertEqual(machine_v2.BUTTON_PINS, (21, 0))
        self.assertEqual(machine_v2.PIXEL_PIN, 42)
        self.assertEqual(machine_v2.BUZZER_PIN, 40)
        self.assertFalse(machine_v2.HAS_TOUCH)
        self.assertTrue(machine_v2.ENABLE_GIFS)
        self.assertFalse(machine_v2.ENABLE_GAME)

    def test_gallery_uses_advance_and_select(self):
        app = FaceApp(self.hardware)
        app._show = lambda: None
        original = app.index
        self.assertIsNone(app.handle_event(("press", "button", "ADVANCE"), 0.0))
        self.assertEqual(app.index, (original + 1) % len(config.FACE_MEDIA))
        self.assertEqual(app.handle_event(("press", "button", "SELECT"), 0.0), "menu")

    def test_menu_selects_led_and_song_items(self):
        app = MenuApp(self.hardware)
        app._draw = lambda: None
        app.index = 1
        self.assertIsNone(app.handle_event(("press", "button", "SELECT"), 0.0))
        self.assertEqual(self.hardware.leds.cycles, 1)
        app.index = 2
        self.assertEqual(
            app.handle_event(("press", "button", "SELECT"), 0.0),
            "song_intro",
        )

    def test_song_uses_advance_and_select(self):
        app = SongApp(self.hardware, "song_intro")
        app._set_state = lambda state: None
        app._update_progress = lambda progress: None
        app._update_levels = lambda levels: None
        self.assertIsNone(app.handle_event(("press", "button", "ADVANCE"), 1.0))
        self.assertTrue(app.player.playing)
        self.assertEqual(
            app.handle_event(("press", "button", "SELECT"), 1.0),
            "menu",
        )


if __name__ == "__main__":
    unittest.main()
