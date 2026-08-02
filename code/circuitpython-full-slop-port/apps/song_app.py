"""Non-blocking song playback with the original MaiMai-style artwork."""

import displayio
import time

import config
from apps.base import App
from apps.songs import SONGS, SONG_TONE_DUTY, SongPlayer
from ui import colors


class SongApp(App):
    UPDATE_INTERVAL = 0.125
    PROGRESS_WIDTH = 72
    PROGRESS_HEIGHT = 5
    LEVEL_WIDTH = 6
    LEVEL_HEIGHT = 20
    LEVEL_PATTERNS = (
        (6, 12, 18, 10),
        (12, 19, 9, 15),
        (18, 8, 14, 20),
        (10, 16, 20, 7),
        (15, 10, 7, 17),
    )

    DISPLAY_TITLES = {
        "song_intro": "MAI INTRO",
        "song_eye": "EYE SONG",
        "song_qzkago": "QZKAGO",
        "song_mario": "MARIO",
    }

    def __init__(self, hardware, song_key):
        super().__init__(hardware)
        self.song_key = song_key
        self.title, self.sequence = SONGS[song_key]
        self.display_title = self.DISPLAY_TITLES.get(song_key, self.title.upper())[:10]
        self.tone_duty = SONG_TONE_DUTY[song_key]
        self.player = SongPlayer(hardware.buzzer)
        self._was_playing = False
        self._state = "stopped"
        self._state_deadline = 0.0
        self._next_ui_update = 0.0
        self._animation_frame = 0
        self._last_progress_width = -1
        self._status_tiles = {}
        self._level_bitmaps = []
        self._progress_bitmap = None

    async def enter(self):
        self._build_screen()
        now = time.monotonic()
        self.player.start(self.sequence, now, self.tone_duty)
        self._was_playing = True
        self._set_state("playing")
        self._update_progress(0.0)
        self._update_levels(self.LEVEL_PATTERNS[0])
        self._next_ui_update = now + self.UPDATE_INTERVAL

    def _build_screen(self):
        display = self.hardware.display
        try:
            group, resources = display.image_group(config.SONG_BACKGROUND)
        except (OSError, ValueError):
            group = display.show_solid(colors.DARK_PURPLE)
            resources = []

        self._append_status_text(group, resources, "PLAYING", 92, 72, "playing")
        self._append_status_text(group, resources, "AGAIN", 100, 80, "again")
        self._append_status_text(group, resources, "TRACK", 100, 70, "track")
        self._append_status_text(group, resources, "CLEAR", 100, 88, "clear")

        title_x = 120 - (len(self.display_title) * 4)
        self._append_text(
            group,
            resources,
            self.display_title,
            title_x,
            145,
            colors.DARK_PURPLE,
        )

        group.append(display.rectangle(72, 5, colors.GREY, 86, 166))
        self._progress_bitmap, progress_tile, owned = self._mutable_tile(
            self.PROGRESS_WIDTH,
            self.PROGRESS_HEIGHT,
            colors.CYAN,
            86,
            166,
        )
        group.append(progress_tile)
        resources.extend(owned)

        for x in (98, 110, 122, 134):
            bitmap, tile, owned = self._mutable_tile(
                self.LEVEL_WIDTH,
                self.LEVEL_HEIGHT,
                colors.CYAN,
                x,
                102,
            )
            self._level_bitmaps.append(bitmap)
            group.append(tile)
            resources.extend(owned)

        group.append(display.rectangle(52, 18, colors.DARK_PURPLE, 48, 198))
        group.append(display.rectangle(56, 18, colors.DARK_PURPLE, 140, 198))
        self._append_text(group, resources, "B MENU", 50, 199, colors.WHITE)
        self._append_text(group, resources, "A AGAIN", 140, 199, colors.WHITE)

        display.set_group(group, resources)

    def _append_status_text(self, group, resources, text, x, y, name):
        tile = self._append_text(group, resources, text, x, y, colors.WHITE)
        tile.hidden = True
        self._status_tiles[name] = tile

    def _append_text(self, group, resources, text, x, y, color):
        tile, owned = self.hardware.display.pixel_text(
            text,
            x,
            y,
            color,
            transparent=True,
        )
        group.append(tile)
        resources.extend(owned)
        return tile

    @staticmethod
    def _mutable_tile(width, height, color, x, y):
        bitmap = displayio.Bitmap(width, height, 2)
        palette = displayio.Palette(2)
        palette[0] = 0
        palette[1] = color
        palette.make_transparent(0)
        tile = displayio.TileGrid(bitmap, pixel_shader=palette, x=x, y=y)
        return bitmap, tile, [bitmap, palette, tile]

    def _set_state(self, state):
        self._state = state
        for tile in self._status_tiles.values():
            tile.hidden = True
        if state == "finished":
            self._status_tiles["track"].hidden = False
            self._status_tiles["clear"].hidden = False
        else:
            self._status_tiles[state].hidden = False

    def _update_progress(self, progress):
        filled_width = min(self.PROGRESS_WIDTH, max(0, int(progress * self.PROGRESS_WIDTH)))
        if filled_width == self._last_progress_width:
            return
        self._last_progress_width = filled_width
        self._progress_bitmap.fill(0)
        for y in range(self.PROGRESS_HEIGHT):
            for x in range(filled_width):
                self._progress_bitmap[x, y] = 1

    def _update_levels(self, heights):
        for bitmap, height in zip(self._level_bitmaps, heights):
            bitmap.fill(0)
            first_row = self.LEVEL_HEIGHT - height
            for y in range(first_row, self.LEVEL_HEIGHT):
                for x in range(self.LEVEL_WIDTH):
                    bitmap[x, y] = 1

    def handle_event(self, event, now):
        kind, source, name = event
        if kind != "press":
            return None
        if (source == "button" and name == "B") or (source == "touch" and name == "L4"):
            return "menu"
        if (source == "button" and name == "A") or (source == "touch" and name == "R4"):
            self.player.start(self.sequence, now, self.tone_duty)
            self._was_playing = True
            self._state_deadline = now + 0.35
            self._set_state("again")
            self._update_progress(0.0)
            self._animation_frame = 0
            self._update_levels(self.LEVEL_PATTERNS[0])
        return None

    def update(self, now):
        playing = self.player.update(now)
        if self._state == "again" and playing and now >= self._state_deadline:
            self._set_state("playing")

        if playing and now >= self._next_ui_update:
            self._update_progress(self.player.progress_at(now))
            pattern = self.LEVEL_PATTERNS[self._animation_frame]
            self._update_levels(pattern)
            self._animation_frame = (self._animation_frame + 1) % len(self.LEVEL_PATTERNS)
            self._next_ui_update = now + self.UPDATE_INTERVAL

        if self._was_playing and not playing:
            self._was_playing = False
            self._set_state("finished")
            self._update_progress(1.0)
            self._update_levels((0, 0, 0, 0))
        return None

    async def exit(self):
        self.player.stop()
        await super().exit()
