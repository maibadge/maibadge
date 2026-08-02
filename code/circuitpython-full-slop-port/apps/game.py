"""Eight-lane MaiBadge rhythm game with scoring and persistent best score."""

import displayio
import time
import vectorio
try:
    import microcontroller
except ImportError:
    microcontroller = None

from apps.base import App
from apps.charts import TUTORIAL_CHART, TUTORIAL_DIFFICULTY, TUTORIAL_TITLE
from ui import colors


SENSOR_DELTAS = (
    (40, -100),
    (100, -40),
    (100, 40),
    (40, 100),
    (-40, 100),
    (-100, 40),
    (-100, -40),
    (-40, -100),
)
PAD_TO_LOCATION = {"R1": 0, "R2": 1, "R3": 2, "R4": 3, "L4": 4, "L3": 5, "L2": 6, "L1": 7}
TRAVEL_TIME = 1.20
PERFECT_WINDOW = 0.075
GREAT_WINDOW = 0.140
GOOD_WINDOW = 0.220
LED_FLASH_SECONDS = 0.075
SCORE_NVM_OFFSET = 1
# The PCB's NeoPixel chain begins two positions clockwise from the touch-pad
# numbering.  Map a logical game lane to the LED physically under that pad.
LED_INDEX_BY_LOCATION = (6, 7, 0, 1, 2, 3, 4, 5)


class GameNote:
    def __init__(self, group, palette, location, hit_time):
        self.location = location
        self.hit_time = hit_time
        self.spawn_time = hit_time - TRAVEL_TIME
        self.state = "pending"
        self.outer = vectorio.Circle(pixel_shader=palette, radius=10, x=-20, y=-20, color_index=2)
        self.inner = vectorio.Circle(pixel_shader=palette, radius=8, x=-20, y=-20, color_index=0)
        group.append(self.outer)
        group.append(self.inner)

    def set_position(self, x, y):
        self.outer.x = x
        self.outer.y = y
        self.inner.x = x
        self.inner.y = y

    def hide(self):
        self.set_position(-20, -20)

    def update_position(self, now):
        if self.state != "pending" or now < self.spawn_time:
            return
        fraction = min(1.0, max(0.0, (now - self.spawn_time) / TRAVEL_TIME))
        dx, dy = SENSOR_DELTAS[self.location]
        self.set_position(120 + int(dx * fraction), 120 + int(dy * fraction))


class GameApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.notes = []
        self.combo = 0
        self.max_combo = 0
        self.score = 0
        self.accuracy_points = 0
        self.hits = 0
        self.misses = 0
        self.finished = False
        self.flash_until = 0
        self.start_time = 0

    async def enter(self):
        display = self.hardware.display
        group = displayio.Group()
        group.append(display.rectangle(240, 240, colors.BLACK))
        palette = displayio.Palette(3)
        palette[0] = colors.BLACK
        palette[1] = colors.WHITE
        palette[2] = colors.YELLOW

        group.append(vectorio.Circle(pixel_shader=palette, radius=108, x=120, y=120, color_index=1))
        group.append(vectorio.Circle(pixel_shader=palette, radius=105, x=120, y=120, color_index=0))
        for dx, dy in SENSOR_DELTAS:
            group.append(vectorio.Circle(pixel_shader=palette, radius=4, x=120 + dx, y=120 + dy, color_index=1))
            group.append(vectorio.Circle(pixel_shader=palette, radius=2, x=120 + dx, y=120 + dy, color_index=0))

        self.combo_label = display.label("0", 112, 124, colors.WHITE, 2)
        self.status_label = display.label("TOUCH TUTORIAL", 68, 62, colors.CYAN)
        self.score_label = display.label("SCORE 000000", 68, 88, colors.WHITE)
        self.detail_label = display.label("EASY  -  GET READY", 52, 166, colors.GREY)
        self.help_label = display.label("L4/B exits", 84, 210, colors.GREY)
        group.append(self.combo_label)
        group.append(self.status_label)
        group.append(self.score_label)
        group.append(self.detail_label)
        group.append(self.help_label)

        self.start_time = time.monotonic() + 2.0
        self.notes = [
            GameNote(group, palette, location, self.start_time + hit_time)
            for hit_time, location in TUTORIAL_CHART
        ]
        display.set_group(group, [palette])
        self._set_centered(self.status_label, TUTORIAL_TITLE, 62)
        self._refresh_score()
        self._set_centered(self.detail_label, "%s  -  GET READY" % TUTORIAL_DIFFICULTY, 166)
        self._set_centered(self.help_label, "L4/B exits", 210)

    def _refresh_score(self):
        self._set_centered(self.combo_label, str(self.combo), 124, 2)
        self._set_centered(self.score_label, "SCORE %06d" % self.score, 88)

    @staticmethod
    def _set_centered(label, text, y, scale=1):
        """Centre a VGA 8-pixel-wide label on the round 240-pixel display."""
        label.text = text
        label.x = max(0, 120 - ((len(text) * 8 * scale) // 2))
        label.y = y

    def _flash_lane(self, location, color, now):
        self.hardware.leds.set_pixel(LED_INDEX_BY_LOCATION[location], color)
        self.flash_until = now + LED_FLASH_SECONDS

    @staticmethod
    def _judgement(delta):
        if delta <= PERFECT_WINDOW:
            return "PERFECT", 1000, 100
        if delta <= GREAT_WINDOW:
            return "GREAT", 700, 70
        if delta <= GOOD_WINDOW:
            return "GOOD", 300, 30
        return None

    def _judge(self, location, now):
        candidate = None
        candidate_delta = GOOD_WINDOW + 1.0
        for note in self.notes:
            if note.state != "pending" or now < note.spawn_time:
                continue
            delta = abs(note.hit_time - now)
            if note.location == location and delta < candidate_delta:
                candidate = note
                candidate_delta = delta

        judgement = self._judgement(candidate_delta) if candidate is not None else None
        if candidate is not None and judgement is not None:
            candidate.state = "hit"
            candidate.hide()
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.hits += 1
            name, points, accuracy = judgement
            self.score += points + (self.combo * 10)
            self.accuracy_points += accuracy
            self._set_centered(self.status_label, name, 62)
            self._set_centered(self.detail_label, "%s  -  %s" % (TUTORIAL_DIFFICULTY, TUTORIAL_TITLE), 166)
            self._flash_lane(location, (0, 32, 16) if name == "PERFECT" else (32, 16, 0), now)
            self.hardware.buzzer.tone(880 if name == "PERFECT" else 660)
            self._refresh_score()
        else:
            self.combo = 0
            self._set_centered(self.status_label, "MISS", 62)
            self._flash_lane(location, (32, 0, 0), now)
            self.hardware.buzzer.tone(180)
            self._refresh_score()

    def handle_event(self, event, now):
        kind, source, name = event
        if kind != "press":
            return None
        if (source == "button" and name == "B") or (
            source == "touch" and name == "L4" and self.finished
        ):
            return "menu"
        if source == "button" and name == "A" and self.finished:
            return "game"
        if source == "touch" and name in PAD_TO_LOCATION and not self.finished:
            self._judge(PAD_TO_LOCATION[name], now)
        return None

    def update(self, now):
        pending = 0
        for note in self.notes:
            if note.state != "pending":
                continue
            if now > note.hit_time + GOOD_WINDOW:
                note.state = "missed"
                note.hide()
                self.combo = 0
                self.misses += 1
                self._set_centered(self.status_label, "MISS", 62)
                self._flash_lane(note.location, (32, 0, 0), now)
                self._refresh_score()
            else:
                pending += 1
                note.update_position(now)

        if not pending and not self.finished:
            self.finished = True
            self.hardware.buzzer.off()
            self.hardware.leds.off()
            accuracy = (self.accuracy_points * 100) // (len(TUTORIAL_CHART) * 100)
            rank = "S" if accuracy >= 95 else "A" if accuracy >= 85 else "B" if accuracy >= 70 else "C"
            best = self._load_best_score()
            if self.score > best:
                self._save_best_score(self.score)
                best = self.score
            self._set_centered(self.status_label, "RESULT %s  %d%%" % (rank, accuracy), 62)
            self._set_centered(self.detail_label, "COMBO %d  BEST %d" % (self.max_combo, best), 166)
            self._set_centered(self.help_label, "A replay  L4/B menu", 210)
        elif self.flash_until and now >= self.flash_until:
            self.hardware.buzzer.off()
            self.hardware.leds.off()
            self.flash_until = 0
        return None

    @staticmethod
    def _load_best_score():
        try:
            return microcontroller.nvm[SCORE_NVM_OFFSET] | (microcontroller.nvm[SCORE_NVM_OFFSET + 1] << 8)
        except (AttributeError, IndexError, TypeError):
            return 0

    @staticmethod
    def _save_best_score(score):
        score = min(65535, int(score))
        try:
            microcontroller.nvm[SCORE_NVM_OFFSET] = score & 0xff
            microcontroller.nvm[SCORE_NVM_OFFSET + 1] = score >> 8
        except (AttributeError, IndexError, TypeError):
            pass
