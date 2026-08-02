"""Full-screen face gallery."""

import gc

import microcontroller

import config
from apps.base import App
from ui import colors


class FaceApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        try:
            saved = microcontroller.nvm[0]
        except (IndexError, TypeError):
            saved = 0
        self.index = saved % len(config.FACE_MEDIA)
        self.gif_active = False

    async def enter(self):
        self._show()

    def _show(self):
        display = self.hardware.display
        filename = config.FACE_MEDIA[self.index]
        display.stop_gif()
        self.gif_active = False
        try:
            if filename.lower().endswith(".gif"):
                display.start_gif(filename)
                self.gif_active = True
            else:
                display.show_image(filename)
        except (OSError, ValueError, MemoryError) as error:
            group = display.show_solid(colors.DARK_PURPLE)
            group.append(display.label("GIF error", 44, 92, colors.RED, 2))
            group.append(display.label(str(error)[:26], 18, 132, colors.WHITE))
            group.append(display.label("Use next or previous", 45, 164, colors.WHITE))
            print("Media error", filename, error)
        try:
            microcontroller.nvm[0] = self.index
        except (IndexError, TypeError):
            pass
        gc.collect()

    def _move(self, amount):
        self.index = (self.index + amount) % len(config.FACE_MEDIA)
        self._show()

    def update(self, now):
        if self.gif_active:
            self.hardware.display.update_gif(now)
        return None

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

    async def exit(self):
        self.hardware.display.stop_gif()
        self.gif_active = False
        await super().exit()
