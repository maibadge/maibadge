"""Translate physical input events into application-level actions."""

import config


def matches(event, action):
    """Return True when a press event matches the active board binding."""
    kind, source, name = event
    if kind != "press":
        return False
    return (source, name) in config.CONTROL_BINDINGS.get(action, ())

