"""Non-blocking song screen."""

import time

from apps.base import App
from apps.songs import SONGS, SongPlayer
from ui import colors


class SongApp(App):
    def __init__(self, hardware, song_key):
        super().__init__(hardware)
        self.song_key = song_key
        self.title, self.sequence = SONGS[song_key]
        self.player = SongPlayer(hardware.buzzer)
        self._was_playing = False

    async def enter(self):
        self._draw("Playing")
        self.player.start(self.sequence, time.monotonic())
        self._was_playing = True

    def _draw(self, state):
        display = self.hardware.display
        group = display.show_solid(colors.DARK_PURPLE)
        group.append(display.label("MaiBadge music", 28, 48, colors.PINK, 2))
        group.append(display.label(self.title[:18], 28, 108, colors.YELLOW, 2))
        group.append(display.label(state, 78, 150, colors.CYAN))
        group.append(display.label("A/R4 restart", 55, 188, colors.WHITE))
        group.append(display.label("B/L4 menu", 63, 210, colors.WHITE))

    def handle_event(self, event, now):
        kind, source, name = event
        if kind != "press":
            return None
        if (source == "button" and name == "B") or (source == "touch" and name == "L4"):
            return "menu"
        if (source == "button" and name == "A") or (source == "touch" and name == "R4"):
            self._draw("Playing")
            self.player.start(self.sequence, now)
            self._was_playing = True
        return None

    def update(self, now):
        playing = self.player.update(now)
        if self._was_playing and not playing:
            self._was_playing = False
            self._draw("Finished")
        return None

    async def exit(self):
        self.player.stop()
        await super().exit()
