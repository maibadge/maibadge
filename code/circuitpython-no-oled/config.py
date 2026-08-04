"""Board configuration for the bear MaiBadge without a display."""

import board

FIRMWARE_NAME = "MaiBadge bear circuitpython-no-oled"
FIRMWARE_VERSION = "0.1.0"
EXPECTED_CIRCUITPYTHON = "10.2.1"

BUTTON_PINS = (board.GPIO9, board.GPIO0)
BUTTON_NAMES = ("LED", "SONG")
BUTTON_ACTIVE_LOW = True
BUTTON_INTERVAL = 0.02

PIXEL_PIN = board.GPIO15
PIXEL_COUNT = 8
PIXEL_BRIGHTNESS = 0.25
ANIMATION_INTERVAL = 0.08

BUZZER_PIN = board.GPIO47
BUZZER_DUTY = 24_000

LOOP_INTERVAL = 0.01
