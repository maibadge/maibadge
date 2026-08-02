"""Host-side tests for code that does not require CircuitPython hardware."""

import os
import sys
import unittest
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from apps.songs import (  # noqa: E402
    QZKAGO,
    SONGS,
    SONG_TONE_DUTY,
    SUPER_MARIO,
    SongPlayer,
    note_frequency,
    parse_rtttl,
)


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

    def test_rtttl_sources_match_micropython(self):
        # These fingerprints are from code/main/apps/maisong.py.  They make
        # normalization or replacement of the original tunes a test failure.
        self.assertEqual(
            hashlib.sha256(SUPER_MARIO.encode()).hexdigest(),
            "68b70ae360908945c221a2a44465bea78fed4bc0637bc2069f611b1092bae604",
        )
        self.assertEqual(
            hashlib.sha256(QZKAGO.encode()).hexdigest(),
            "ba7518659f595fb12b4c3d54130ba0d38c197f3c15e26bbe060c73a68efb8e1e",
        )

    def test_all_songs_are_nonempty(self):
        for name, sequence in SONGS.values():
            self.assertTrue(name)
            self.assertGreater(len(sequence), 5)
            for frequency, duration in sequence:
                self.assertGreaterEqual(frequency, 0)
                self.assertGreater(duration, 0)

    def test_legacy_articulation_is_preserved(self):
        self.assertEqual(SONG_TONE_DUTY["song_intro"], 1.0)
        self.assertEqual(SONG_TONE_DUTY["song_eye"], 1.0)
        self.assertEqual(SONG_TONE_DUTY["song_qzkago"], 0.9)
        self.assertEqual(SONG_TONE_DUTY["song_mario"], 0.9)

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
        self.assertTrue(player.completed)
        self.assertEqual(player.progress, 1.0)

    def test_player_reports_progress_without_changing_sequence(self):
        buzzer = FakeBuzzer()
        player = SongPlayer(buzzer)
        sequence = ((440, 1.0), (880, 1.0))
        player.start(sequence, 10.0)
        self.assertEqual(player.sequence, sequence)
        self.assertAlmostEqual(player.progress_at(10.5), 0.25)
        player.update(10.9)
        player.update(11.0)
        self.assertAlmostEqual(player.progress_at(11.5), 0.75)

    def test_full_duty_sequence_has_no_inserted_gap(self):
        buzzer = FakeBuzzer()
        player = SongPlayer(buzzer)
        player.start(((440, 1.0), (880, 1.0)), 10.0, tone_duty=1.0)
        player.update(11.0)
        self.assertEqual(buzzer.calls[-1], ("tone", 880))


if __name__ == "__main__":
    unittest.main()
