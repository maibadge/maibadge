"""Main application launcher."""

import config
from apps.base import App
from ui import colors


class MenuApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.index = 0

    async def enter(self):
        self._draw()

    def _draw(self):
        display = self.hardware.display
        try:
            group, resources = display.image_group(config.MENU_BACKGROUND)
        except (OSError, ValueError):
            group = display.show_solid(colors.DARK_PURPLE)
            resources = []

        # Match the original MicroPython menu composition pixel-for-pixel:
        # one 57x96 selected card, up to four 35x59 neighbours, and VGA 8x16.
        self._append_image(group, resources, config.MENU_ITEM_SELECTED, 92, 88)

        if self.index >= 1:
            self._append_small(group, resources, self.index - 1, 52)
        if self.index >= 2:
            self._append_small(group, resources, self.index - 2, 12)
        if len(config.MENU_ITEMS) - 1 - self.index >= 1:
            self._append_small(group, resources, self.index + 1, 153)
        if len(config.MENU_ITEMS) - 1 - self.index >= 2:
            self._append_small(group, resources, self.index + 2, 193)

        current = config.MENU_ITEMS[self.index][0]
        self._append_text(group, resources, current[:4], 102, 103)
        if len(current) > 4:
            self._append_text(group, resources, current[4:], 102, 119)
        display.set_group(group, resources)

    def _append_image(self, group, resources, filename, x, y):
        tile, owned = self.hardware.display.image_tile(filename, x, y)
        group.append(tile)
        resources.extend(owned)

    def _append_small(self, group, resources, item_index, x):
        self._append_image(group, resources, config.MENU_ITEM_SMALL, x, 97)
        self._append_text(group, resources, config.MENU_ITEMS[item_index][0][:4], x + 2, 108)

    def _append_text(self, group, resources, text, x, y):
        tile, owned = self.hardware.display.pixel_text(text, x, y, colors.WHITE, colors.BLACK)
        group.append(tile)
        resources.extend(owned)

    def _move(self, amount):
        self.index = (self.index + amount) % len(config.MENU_ITEMS)
        self._draw()

    def handle_event(self, event, now):
        del now
        kind, source, name = event
        if kind != "press":
            return None
        if (source == "touch" and name == "R3") or (source == "button" and name == "A"):
            self._move(1)
        elif source == "touch" and name == "L3":
            self._move(-1)
        elif source == "button" and name == "B":
            return "face"
        elif source == "touch" and name == "R4":
            action = config.MENU_ITEMS[self.index][1]
            if action == "led":
                self.hardware.leds.next_color()
                return None
            return action
        return None
