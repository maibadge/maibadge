"""Host-side tests for code that does not require CircuitPython hardware."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from apps.songs import SONGS, SongPlayer, note_frequency, parse_rtttl  # noqa: E402


class FakeBuzzer:
    def __init__(self):
        self.calls = []

    def tone(self, frequency):
        self.calls.append(("tone", frequency))

    def off(self):
        self.calls.append(("off", 0))


class SongTests(unittest.TestCase):
    def test_reference_pitch(self):
        self.assertEqual(note_frequency("A4"), 440)
        self.assertEqual(note_frequency("REST"), 0)
        self.assertTrue(260 <= note_frequency("C4") <= 263)

    def test_rtttl_duration_and_notes(self):
        sequence = parse_rtttl("test:d=4,o=5,b=120:c,8d.,p")
        self.assertEqual(len(sequence), 3)
        self.assertEqual(sequence[2][0], 0)
        self.assertAlmostEqual(sequence[0][1], 0.5)
        self.assertAlmostEqual(sequence[1][1], 0.375)

    def test_all_songs_are_nonempty(self):
        for name, sequence in SONGS.values():
            self.assertTrue(name)
            self.assertGreater(len(sequence), 5)
            for frequency, duration in sequence:
                self.assertGreaterEqual(frequency, 0)
                self.assertGreater(duration, 0)

    def test_player_advances_without_blocking(self):
        buzzer = FakeBuzzer()
        player = SongPlayer(buzzer)
        player.start(((440, 1.0), (0, 0.5)), 10.0)
        self.assertTrue(player.playing)
        self.assertEqual(buzzer.calls[-1], ("tone", 440))
        player.update(10.9)
        self.assertEqual(buzzer.calls[-1], ("off", 0))
        player.update(11.0)
        self.assertEqual(buzzer.calls[-1], ("tone", 0))
        player.update(11.45)
        player.update(11.5)
        self.assertFalse(player.playing)


if __name__ == "__main__":
    unittest.main()
