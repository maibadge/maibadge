"""Live input, memory, and firmware diagnostics."""

import gc
import sys

import config
from apps.base import App
from ui import colors


class DiagnosticsApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.labels = []
        self.next_refresh = 0.0

    async def enter(self):
        display = self.hardware.display
        group = display.show_solid(colors.BLACK)
        group.append(display.label("MaiBadge diagnostics", 8, 18, colors.CYAN, 2))
        group.append(display.label(config.EXPECTED_BOARD_ID, 8, 43, colors.GREY))
        for index, _ in enumerate(config.TOUCH_CONFIG):
            label = display.label("", 8, 68 + index * 16, colors.WHITE)
            self.labels.append(label)
            group.append(label)
        self.memory_label = display.label("", 8, 204, colors.YELLOW)
        group.append(self.memory_label)
        group.append(display.label("B/L4 returns", 8, 224, colors.PINK))

    def handle_event(self, event, now):
        del now
        kind, source, name = event
        if kind == "press" and (
            (source == "button" and name == "B") or (source == "touch" and name == "L4")
        ):
            return "menu"
        return None

    def update(self, now):
        if now < self.next_refresh:
            return None
        self.next_refresh = now + 0.20
        for label, snapshot in zip(self.labels, self.hardware.touch.snapshot()):
            name, raw, baseline, threshold, pressed = snapshot
            label.text = "%s %5d base %5d %s" % (
                name,
                raw,
                baseline,
                "TOUCH" if pressed else "",
            )
            del threshold
        self.memory_label.text = "heap %d  CP %s" % (gc.mem_free(), sys.implementation.version[0])
        return None
