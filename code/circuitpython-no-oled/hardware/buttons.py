"""Debounced two-button input using CircuitPython's keypad scanner."""

import keypad

import config


class Buttons:
    def __init__(self):
        self._keys = keypad.Keys(
            config.BUTTON_PINS,
            value_when_pressed=not config.BUTTON_ACTIVE_LOW,
            pull=True,
            interval=config.BUTTON_INTERVAL,
        )

    def poll(self):
        events = []
        event = self._keys.events.get()
        while event is not None:
            name = config.BUTTON_NAMES[event.key_number]
            events.append(("press" if event.pressed else "release", name))
            event = self._keys.events.get()
        return events

    def deinit(self):
        self._keys.deinit()
