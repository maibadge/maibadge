"""Host-side tests for the merged headless UI mode."""

import os
import importlib.util
import subprocess
import sys
import types
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

fake_board = sys.modules.setdefault("board", types.SimpleNamespace())
for pin_number in range(49):
    setattr(fake_board, "GPIO" + str(pin_number), pin_number)

import config  # noqa: E402
from apps.headless import HeadlessApp, SONG_ORDER  # noqa: E402


class FakeLeds:
    def __init__(self):
        self.mode = "off"
        self.updated_at = []
        self.off_count = 0

    def next_mode(self, now):
        del now
        self.mode = "red" if self.mode == "off" else "off"
        return self.mode

    def update(self, now):
        self.updated_at.append(now)

    def off(self):
        self.off_count += 1


class FakeBuzzer:
    def __init__(self):
        self.history = []

    def tone(self, frequency):
        self.history.append(frequency)

    def off(self):
        self.history.append(0)


class FakeHardware:
    def __init__(self):
        self.leds = FakeLeds()
        self.buzzer = FakeBuzzer()

    def safe_outputs(self):
        self.buzzer.off()


class HeadlessAppTests(unittest.TestCase):
    def test_bear_buttons_cycle_leds_and_songs(self):
        hardware = FakeHardware()
        app = HeadlessApp(hardware)
        app.handle_event(("press", "button", "A"), 1.0)
        self.assertEqual(hardware.leds.mode, "red")

        app.handle_event(("press", "button", "B"), 2.0)
        self.assertEqual(app.song_index, 0)
        self.assertEqual(SONG_ORDER[app.song_index], "song_intro")
        self.assertTrue(app.player.playing)

        app.update(2.1)
        self.assertEqual(hardware.leds.updated_at, [2.1])

    def test_machine_headless_bindings_are_present(self):
        from boards import machine_v2

        self.assertEqual(
            machine_v2.CONTROL_BINDINGS["headless_led"],
            (("button", "ADVANCE"),),
        )
        self.assertEqual(
            machine_v2.CONTROL_BINDINGS["headless_song"],
            (("button", "SELECT"),),
        )
        original = config.CONTROL_BINDINGS
        try:
            config.CONTROL_BINDINGS = machine_v2.CONTROL_BINDINGS
            hardware = FakeHardware()
            app = HeadlessApp(hardware)
            app.handle_event(("press", "button", "ADVANCE"), 1.0)
            app.handle_event(("press", "button", "SELECT"), 2.0)
            self.assertEqual(hardware.leds.mode, "red")
            self.assertTrue(app.player.playing)
        finally:
            config.CONTROL_BINDINGS = original

    def test_headless_controller_imports_without_display_modules(self):
        script = """
import sys, types
board = types.SimpleNamespace()
for number in range(49):
    setattr(board, 'GPIO' + str(number), number)
sys.modules['board'] = board
class Events:
    def get(self): return None
class Keys:
    def __init__(self, *args, **kwargs): self.events = Events()
    def deinit(self): pass
class PWMOut:
    def __init__(self, *args, **kwargs): self.frequency = 440; self.duty_cycle = 0
    def deinit(self): pass
class Pixels:
    def __init__(self, pin, count, **kwargs): self.values = [(0, 0, 0)] * count
    def __setitem__(self, index, value): self.values[index] = value
    def fill(self, value): self.values = [value] * len(self.values)
    def show(self): pass
    def deinit(self): pass
sys.modules['keypad'] = types.SimpleNamespace(Keys=Keys)
sys.modules['pwmio'] = types.SimpleNamespace(PWMOut=PWMOut)
sys.modules['neopixel'] = types.SimpleNamespace(NeoPixel=Pixels)
import config
import apps.controller
from hardware import BadgeHardware
hardware = BadgeHardware()
assert config.UI_MODE == 'headless'
assert config.HAS_DISPLAY is False
assert config.HAS_TOUCH is False
assert hardware.display is None
assert 'hardware.display' not in sys.modules
print('headless import OK')
"""
        environment = os.environ.copy()
        environment["MAIBADGE_UI"] = "headless"
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("headless import OK", result.stdout)


class FakePixels:
    def __init__(self, _pin, count, **_kwargs):
        self.values = [(0, 0, 0)] * count
        self.show_count = 0

    def __setitem__(self, index, value):
        self.values[index] = value

    def fill(self, value):
        self.values = [value] * len(self.values)

    def show(self):
        self.show_count += 1

    def deinit(self):
        pass


class LedAnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.modules["neopixel"] = types.SimpleNamespace(NeoPixel=FakePixels)
        spec = importlib.util.spec_from_file_location(
            "headless_shared_leds", os.path.join(ROOT, "hardware", "leds.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.Leds = module.Leds

    def test_modes_wrap_and_start_off(self):
        leds = self.Leds()
        self.assertEqual(leds.mode_name, "off")
        names = [leds.next_mode(float(index)) for index in range(len(leds.MODES))]
        self.assertEqual(names[0], "red")
        self.assertEqual(names[-1], "off")

    def test_animation_updates_only_after_deadline(self):
        leds = self.Leds()
        while leds.mode_name != "rainbow":
            leds.next_mode(1.0)
        initial_frame = leds.frame
        leds.update(0.9)
        self.assertEqual(leds.frame, initial_frame)
        leds.update(1.0)
        self.assertEqual(leds.frame, initial_frame + 1)


if __name__ == "__main__":
    unittest.main()
