"""Aggregate and own every MaiBadge peripheral exactly once."""

import config

from hardware.buttons import Buttons
from hardware.buzzer import Buzzer
from hardware.leds import Leds


class NoTouchPads:
    """No-op touch interface used by boards without touch electrodes."""

    async def calibrate(self):
        return

    def poll(self):
        return []

    def snapshot(self):
        return ()

    def deinit(self):
        return


class BadgeHardware:
    def __init__(self):
        self.display = None
        if config.HAS_DISPLAY:
            # Import lazily so headless installs do not require display modules.
            from hardware.display import Display

            self.display = Display()
        self.buttons = Buttons()
        if config.HAS_TOUCH:
            from hardware.touch import TouchPads

            self.touch = TouchPads()
        else:
            self.touch = NoTouchPads()
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
        if self.display is not None:
            self.display.deinit()
