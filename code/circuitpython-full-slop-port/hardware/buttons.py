"""Debounced button events using CircuitPython's native keypad scanner."""

import keypad

import config


class Buttons:
    def __init__(self):
        self._keys = keypad.Keys(
            config.BUTTON_PINS,
            value_when_pressed=not config.BUTTON_ACTIVE_LOW,
            pull=True,
            interval=0.02,
        )

    def poll(self):
        result = []
        event = self._keys.events.get()
        while event is not None:
            name = config.BUTTON_NAMES[event.key_number]
            result.append(("press" if event.pressed else "release", "button", name))
            event = self._keys.events.get()
        return result

    def deinit(self):
        self._keys.deinit()
