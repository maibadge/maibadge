"""Host-side tests for hardware-independent no-OLED firmware logic."""

import importlib.util
import pathlib
import sys
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_songs():
    spec = importlib.util.spec_from_file_location("no_oled_songs", ROOT / "songs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_leds():
    fake_config = types.SimpleNamespace(
        PIXEL_PIN=15,
        PIXEL_COUNT=8,
        PIXEL_BRIGHTNESS=0.25,
        ANIMATION_INTERVAL=0.08,
    )

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

    fake_neopixel = types.SimpleNamespace(NeoPixel=FakePixels)
    old_config = sys.modules.get("config")
    old_neopixel = sys.modules.get("neopixel")
    sys.modules["config"] = fake_config
    sys.modules["neopixel"] = fake_neopixel
    try:
        spec = importlib.util.spec_from_file_location("no_oled_leds", ROOT / "hardware" / "leds.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old_config is None:
            del sys.modules["config"]
        else:
            sys.modules["config"] = old_config
        if old_neopixel is None:
            del sys.modules["neopixel"]
        else:
            sys.modules["neopixel"] = old_neopixel


class FakeBuzzer:
    def __init__(self):
        self.frequency = 0
        self.history = []

    def tone(self, frequency):
        self.frequency = frequency
        self.history.append(frequency)

    def off(self):
        self.frequency = 0
        self.history.append(0)


class SongTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.songs = load_songs()

    def test_song_order_and_content(self):
        self.assertEqual(
            [item[0] for item in self.songs.SONGS],
            ["Mai Intro", "Eye Song", "QZKago", "Super Mario"],
        )
        for _title, sequence, _tone_fraction in self.songs.SONGS:
            self.assertGreater(len(sequence), 20)
            self.assertTrue(all(duration > 0 for _frequency, duration in sequence))

    def test_note_frequency(self):
        self.assertEqual(self.songs.note_frequency("A4"), 440)
        self.assertEqual(self.songs.note_frequency("REST"), 0)
        self.assertEqual(self.songs.note_frequency("0"), 0)

    def test_player_is_non_blocking_and_can_be_replaced(self):
        buzzer = FakeBuzzer()
        player = self.songs.SongPlayer(buzzer)
        first = ((440, 1.0), (660, 1.0))
        second = ((880, 0.5),)
        player.start(first, 10.0, 0.9)
        self.assertEqual(buzzer.frequency, 440)
        self.assertTrue(player.playing)
        player.update(10.5)
        self.assertEqual(buzzer.frequency, 440)
        player.start(second, 10.5, 0.9)
        self.assertEqual(buzzer.frequency, 880)
        player.update(10.96)
        self.assertEqual(buzzer.frequency, 0)
        player.update(11.02)
        self.assertFalse(player.playing)


class LedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.leds_module = load_leds()

    def test_modes_wrap_and_start_off(self):
        leds = self.leds_module.Leds()
        self.assertEqual(leds.mode_name, "off")
        names = [leds.next_mode(float(index)) for index in range(len(leds.MODES))]
        self.assertEqual(names[0], "red")
        self.assertEqual(names[-1], "off")

    def test_animation_updates_only_after_deadline(self):
        leds = self.leds_module.Leds()
        while leds.mode_name != "rainbow":
            leds.next_mode(1.0)
        initial_frame = leds.frame
        leds.update(0.9)
        self.assertEqual(leds.frame, initial_frame)
        leds.update(1.0)
        self.assertEqual(leds.frame, initial_frame + 1)


if __name__ == "__main__":
    unittest.main()
