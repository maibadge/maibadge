"""Full-screen face gallery."""

import gc

import microcontroller

import config
from apps.base import App


class FaceApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        try:
            saved = microcontroller.nvm[0]
        except (IndexError, TypeError):
            saved = 0
        self.index = saved % len(config.FACE_IMAGES)

    async def enter(self):
        self._show()

    def _show(self):
        self.hardware.display.show_image(config.FACE_IMAGES[self.index])
        try:
            microcontroller.nvm[0] = self.index
        except (IndexError, TypeError):
            pass
        gc.collect()

    def _move(self, amount):
        self.index = (self.index + amount) % len(config.FACE_IMAGES)
        self._show()

    def handle_event(self, event, now):
        del now
        kind, source, name = event
        if kind != "press":
            return None
        if (source == "touch" and name == "R3") or (source == "button" and name == "A"):
            self._move(1)
        elif source == "touch" and name == "L3":
            self._move(-1)
        elif (source == "touch" and name == "L4") or (source == "button" and name == "B"):
            return "menu"
        return None
