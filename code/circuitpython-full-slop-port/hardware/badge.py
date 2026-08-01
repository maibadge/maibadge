"""Aggregate and own every MaiBadge peripheral exactly once."""

from hardware.buttons import Buttons
from hardware.buzzer import Buzzer
from hardware.display import Display
from hardware.leds import Leds
from hardware.touch import TouchPads


class BadgeHardware:
    def __init__(self):
        # Display first so initialization failures remain easy to diagnose.
        self.display = Display()
        self.buttons = Buttons()
        self.touch = TouchPads()
        self.buzzer = Buzzer()
        self.leds = Leds()

    async def calibrate(self):
        await self.touch.calibrate()

    def poll_events(self):
        events = self.buttons.poll()
        events.extend(self.touch.poll())
        return events

    def safe_outputs(self):
        self.buzzer.off()

    def deinit(self):
        self.safe_outputs()
        self.buttons.deinit()
        self.touch.deinit()
        self.buzzer.deinit()
        self.leds.deinit()
        self.display.deinit()
