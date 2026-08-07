"""Two-button LED and music mode for badges without a display."""

import controls
from apps.base import App
from apps.songs import SONGS, SONG_TONE_DUTY, SongPlayer


SONG_ORDER = ("song_intro", "song_eye", "song_qzkago", "song_mario")


class HeadlessApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.song_index = -1
        self.player = SongPlayer(hardware.buzzer)

    async def enter(self):
        print("Headless mode: LED button cycles modes; song button starts next song")

    def handle_event(self, event, now):
        if controls.matches(event, "headless_led"):
            mode = self.hardware.leds.next_mode(now)
            print("LED mode:", mode)
        elif controls.matches(event, "headless_song"):
            self.song_index = (self.song_index + 1) % len(SONG_ORDER)
            key = SONG_ORDER[self.song_index]
            title, sequence = SONGS[key]
            self.player.start(sequence, now, SONG_TONE_DUTY[key])
            print("Playing:", title)
        return None

    def update(self, now):
        self.hardware.leds.update(now)
        self.player.update(now)
        return None

    async def exit(self):
        self.player.stop()
        self.hardware.leds.off()
        await super().exit()

