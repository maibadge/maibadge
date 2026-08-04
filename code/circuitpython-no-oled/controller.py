"""Two-button no-display application loop."""

import time

import config
from songs import SONGS, SongPlayer


class Controller:
    def __init__(self, hardware):
        self.hardware = hardware
        self.song_index = -1
        self.player = SongPlayer(hardware.buzzer)

    def handle_event(self, event, now):
        kind, name = event
        if kind != "press":
            return
        if name == "LED":
            mode = self.hardware.leds.next_mode(now)
            print("LED mode:", mode)
        elif name == "SONG":
            self.song_index = (self.song_index + 1) % len(SONGS)
            title, sequence, tone_fraction = SONGS[self.song_index]
            self.player.start(sequence, now, tone_fraction)
            print("Playing:", title)

    def run(self):
        print("Button 1: LED mode; Button 2: next song")
        while True:
            now = time.monotonic()
            for event in self.hardware.poll_events():
                self.handle_event(event, now)
            self.hardware.leds.update(now)
            self.player.update(now)
            time.sleep(config.LOOP_INTERVAL)
