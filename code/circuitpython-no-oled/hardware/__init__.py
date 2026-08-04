"""Own all no-display badge peripherals exactly once."""

from hardware.buttons import Buttons
from hardware.buzzer import Buzzer
from hardware.leds import Leds


class BadgeHardware:
    def __init__(self):
        self.buttons = Buttons()
        self.buzzer = Buzzer()
        self.leds = Leds()

    def poll_events(self):
        return self.buttons.poll()

    def safe_outputs(self):
        self.buzzer.off()
        self.leds.off()

    def deinit(self):
        self.safe_outputs()
        self.buttons.deinit()
        self.buzzer.deinit()
        self.leds.deinit()
