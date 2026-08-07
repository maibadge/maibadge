"""Live input, memory, and firmware diagnostics."""

import gc
import sys

import config
import controls
from apps.base import App
from ui import colors


class DiagnosticsApp(App):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.labels = []
        self.event_label = None
        self.next_refresh = 0.0

    async def enter(self):
        display = self.hardware.display
        group = display.show_solid(colors.BLACK)
        group.append(display.label("MaiBadge diagnostics", 8, 18, colors.CYAN, 2))
        group.append(display.label(config.EXPECTED_BOARD_ID, 8, 43, colors.GREY))
        if config.HAS_TOUCH:
            for index, _ in enumerate(config.TOUCH_CONFIG):
                label = display.label("", 8, 68 + index * 16, colors.WHITE)
                self.labels.append(label)
                group.append(label)
        else:
            group.append(display.label("ADVANCE GPIO21", 8, 72, colors.WHITE))
            group.append(display.label("SELECT  GPIO0", 8, 94, colors.WHITE))
            group.append(display.label("LED GPIO42", 8, 122, colors.GREY))
            group.append(display.label("BUZZ GPIO40", 8, 144, colors.GREY))
            self.event_label = display.label("event: none", 8, 174, colors.PINK)
            group.append(self.event_label)
        self.memory_label = display.label("", 8, 204, colors.YELLOW)
        group.append(self.memory_label)
        group.append(
            display.label(config.CONTROL_LABELS["diagnostics_back"], 8, 224, colors.PINK)
        )

    def handle_event(self, event, now):
        del now
        if self.event_label is not None:
            kind, source, name = event
            self.event_label.text = "event: %s %s %s" % (kind, source, name)
        if controls.matches(event, "diagnostics_back"):
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
