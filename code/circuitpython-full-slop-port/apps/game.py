"""Repaired monotonic-time rhythm game."""

import displayio
import time
import vectorio

from apps.base import App
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
CHART = (7, 0, 7, 0, 7, 0, 7, 0, 1, 2, 3, 4, 5, 6, 7)
SPAWN_INTERVAL = 0.20
TRAVEL_TIME = 1.20
HIT_WINDOW = 0.22


class GameNote:
    def __init__(self, group, palette, location, spawn_time):
        self.location = location
        self.spawn_time = spawn_time
        self.hit_time = spawn_time + TRAVEL_TIME
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
        self.hits = 0
        self.misses = 0
        self.finished = False

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

        self.combo_label = display.label("0", 108, 124, colors.WHITE, 2)
        self.status_label = display.label("Get ready", 75, 18, colors.CYAN)
        self.help_label = display.label("B exits", 93, 232, colors.GREY)
        group.append(self.combo_label)
        group.append(self.status_label)
        group.append(self.help_label)

        start = time.monotonic() + 1.5
        self.notes = [
            GameNote(group, palette, location, start + index * SPAWN_INTERVAL)
            for index, location in enumerate(CHART)
        ]
        display.set_group(group, [palette])

    def _refresh_score(self):
        self.combo_label.text = str(self.combo)

    def _judge(self, location, now):
        candidate = None
        candidate_delta = HIT_WINDOW + 1.0
        for note in self.notes:
            if note.state != "pending" or now < note.spawn_time:
                continue
            delta = abs(note.hit_time - now)
            if note.location == location and delta < candidate_delta:
                candidate = note
                candidate_delta = delta

        if candidate is not None and candidate_delta <= HIT_WINDOW:
            candidate.state = "hit"
            candidate.hide()
            self.combo += 1
            self.hits += 1
            self.status_label.text = "Perfect" if candidate_delta <= 0.09 else "Good"
            self._refresh_score()
        else:
            self.combo = 0
            self.status_label.text = "Miss"
            self._refresh_score()

    def handle_event(self, event, now):
        kind, source, name = event
        if kind != "press":
            return None
        if source == "button" and name == "B":
            return "menu"
        if source == "touch" and name in PAD_TO_LOCATION and not self.finished:
            self._judge(PAD_TO_LOCATION[name], now)
        return None

    def update(self, now):
        pending = 0
        for note in self.notes:
            if note.state != "pending":
                continue
            if now > note.hit_time + HIT_WINDOW:
                note.state = "missed"
                note.hide()
                self.combo = 0
                self.misses += 1
                self.status_label.text = "Miss"
                self._refresh_score()
            else:
                pending += 1
                note.update_position(now)

        if not pending and not self.finished:
            self.finished = True
            self.status_label.text = "%d hit  %d miss" % (self.hits, self.misses)
            self.help_label.text = "B returns to menu"
        return None
