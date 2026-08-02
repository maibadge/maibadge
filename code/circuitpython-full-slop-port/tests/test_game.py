"""Host checks for the rhythm game's chart, timing grades, and saved score."""

import os
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

fake_board = types.SimpleNamespace()
for pin_number in range(49):
    setattr(fake_board, "GPIO" + str(pin_number), pin_number)
sys.modules.setdefault("board", fake_board)
sys.modules.setdefault("microcontroller", types.SimpleNamespace(nvm=bytearray(3)))


class FakeGroup(list):
    pass


class FakePalette:
    def __init__(self, size):
        self.colors = [0] * size

    def __setitem__(self, index, color):
        self.colors[index] = color


class FakeCircle:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


sys.modules.setdefault("displayio", types.SimpleNamespace(Group=FakeGroup, Palette=FakePalette))
sys.modules.setdefault("vectorio", types.SimpleNamespace(Circle=FakeCircle))

from apps.charts import TUTORIAL_CHART  # noqa: E402
from apps.game import LED_INDEX_BY_LOCATION, GameApp, GOOD_WINDOW, GREAT_WINDOW, PERFECT_WINDOW  # noqa: E402


class GameTests(unittest.TestCase):
    def test_tutorial_chart_is_ordered_and_uses_all_lanes(self):
        self.assertEqual(tuple(sorted(TUTORIAL_CHART)), TUTORIAL_CHART)
        self.assertEqual({location for _, location in TUTORIAL_CHART}, set(range(8)))

    def test_lane_led_mapping_compensates_for_the_two_step_clockwise_offset(self):
        self.assertEqual(LED_INDEX_BY_LOCATION, (6, 7, 0, 1, 2, 3, 4, 5))

    def test_judgement_windows_have_expected_scores(self):
        self.assertEqual(GameApp._judgement(PERFECT_WINDOW), ("PERFECT", 1000, 100))
        self.assertEqual(GameApp._judgement(GREAT_WINDOW), ("GREAT", 700, 70))
        self.assertEqual(GameApp._judgement(GOOD_WINDOW), ("GOOD", 300, 30))
        self.assertIsNone(GameApp._judgement(GOOD_WINDOW + 0.001))

    def test_best_score_round_trips_through_nvm(self):
        GameApp._save_best_score(12345)
        self.assertEqual(GameApp._load_best_score(), 12345)

    def test_l4_exits_only_from_results_while_button_b_always_exits(self):
        hardware = types.SimpleNamespace(
            leds=types.SimpleNamespace(set_pixel=lambda index, color: None),
            buzzer=types.SimpleNamespace(tone=lambda frequency: None),
        )
        app = GameApp(hardware)
        app.status_label = types.SimpleNamespace(text="", x=0, y=0)
        app.combo_label = types.SimpleNamespace(text="", x=0, y=0)
        app.score_label = types.SimpleNamespace(text="", x=0, y=0)
        self.assertIsNone(app.handle_event(("press", "touch", "L4"), 0.0))
        self.assertEqual(app.handle_event(("press", "button", "B"), 0.0), "menu")
        app.finished = True
        self.assertEqual(app.handle_event(("press", "touch", "L4"), 0.0), "menu")


if __name__ == "__main__":
    unittest.main()
