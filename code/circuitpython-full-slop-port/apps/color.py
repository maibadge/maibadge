"""Full-screen two-colour display using the MaiBadge reference shades."""

import microcontroller

import controls
from apps.base import App
from ui import colors


SCREEN_COLORS = (colors.BADGE_BLUE, colors.BADGE_RED)
NVM_OFFSET = 3


class ColorApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        try:
            saved = microcontroller.nvm[NVM_OFFSET]
        except (IndexError, TypeError):
            saved = 0
        # Erased ESP32 NVM can read as 255; treat any unknown value as blue.
        self.index = saved if saved < len(SCREEN_COLORS) else 0

    async def enter(self):
        self._show()

    def _show(self):
        self.hardware.display.show_solid(SCREEN_COLORS[self.index])
        try:
            microcontroller.nvm[NVM_OFFSET] = self.index
        except (IndexError, TypeError):
            pass

    def _move(self, amount):
        self.index = (self.index + amount) % len(SCREEN_COLORS)
        self._show()

    def handle_event(self, event, now):
        del now
        if controls.matches(event, "face_next"):
            self._move(1)
        elif controls.matches(event, "face_previous"):
            self._move(-1)
        elif controls.matches(event, "face_menu"):
            return "menu"
        return None
