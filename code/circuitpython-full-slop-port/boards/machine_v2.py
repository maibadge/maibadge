"""Machine-shaped MaiBadge PCB hardware profile."""

import board


NAME = "machine_v2"
# The connected machine badge was verified as a YD ESP32-S3 N16R8.
EXPECTED_BOARD_ID = "yd_esp32_s3_n16r8"

DISPLAY_CLOCK = board.GPIO14
DISPLAY_MOSI = board.GPIO13
DISPLAY_DC = board.GPIO10
DISPLAY_CS = board.GPIO11
DISPLAY_RESET = board.GPIO12

PIXEL_PIN = board.GPIO42
BUZZER_PIN = board.GPIO40
BUTTON_PINS = (board.GPIO21, board.GPIO0)
BUTTON_NAMES = ("ADVANCE", "SELECT")

HAS_TOUCH = False
ENABLE_GIFS = True
ENABLE_GAME = False
ENABLE_DIAGNOSTICS = True
STARTUP_STATUS = "STARTING"
TOUCH_CONFIG = ()

CONTROL_BINDINGS = {
    "face_next": (("button", "ADVANCE"),),
    "face_previous": (),
    "face_menu": (("button", "SELECT"),),
    "menu_next": (("button", "ADVANCE"),),
    "menu_previous": (),
    "menu_select": (("button", "SELECT"),),
    "menu_back": (),
    "song_replay": (("button", "ADVANCE"),),
    "song_back": (("button", "SELECT"),),
    "diagnostics_back": (("button", "SELECT"),),
    "game_exit": (),
    "game_exit_finished": (),
    "game_replay": (),
}

GAME_LANE_BINDINGS = {}

CONTROL_LABELS = {
    "song_back": "SELECT MENU",
    "song_replay": "ADV AGAIN",
    "diagnostics_back": "SELECT returns",
}
