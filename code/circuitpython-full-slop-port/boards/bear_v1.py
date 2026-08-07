"""Original bear-shaped MaiBadge hardware profile."""

import board


NAME = "bear_v1"
EXPECTED_BOARD_ID = "yd_esp32_s3_n16r8"

DISPLAY_CLOCK = board.GPIO14
DISPLAY_MOSI = board.GPIO13
DISPLAY_DC = board.GPIO10
DISPLAY_CS = board.GPIO11
DISPLAY_RESET = board.GPIO12

PIXEL_PIN = board.GPIO15
BUZZER_PIN = board.GPIO47
BUTTON_PINS = (board.GPIO9, board.GPIO0)
BUTTON_NAMES = ("A", "B")

HAS_TOUCH = True
ENABLE_GIFS = True
ENABLE_GAME = True
ENABLE_DIAGNOSTICS = True
STARTUP_STATUS = "CALIBRATING"

TOUCH_CONFIG = (
    ("R1", board.GPIO1),
    ("L1", board.GPIO2),
    ("L3", board.GPIO3),
    ("R3", board.GPIO4),
    ("R2", board.GPIO5),
    ("R4", board.GPIO6),
    ("L4", board.GPIO7),
    ("L2", board.GPIO8),
)

CONTROL_BINDINGS = {
    "face_next": (("touch", "R3"), ("button", "A")),
    "face_previous": (("touch", "L3"),),
    "face_menu": (("touch", "L4"), ("button", "B")),
    "menu_next": (("touch", "R3"), ("button", "A")),
    "menu_previous": (("touch", "L3"),),
    "menu_select": (("touch", "R4"),),
    "menu_back": (("button", "B"),),
    "song_replay": (("touch", "R4"), ("button", "A")),
    "song_back": (("touch", "L4"), ("button", "B")),
    "diagnostics_back": (("touch", "L4"), ("button", "B")),
    "game_exit": (("button", "B"),),
    "game_exit_finished": (("touch", "L4"),),
    "game_replay": (("button", "A"),),
}

GAME_LANE_BINDINGS = {
    ("touch", "R1"): 0,
    ("touch", "R2"): 1,
    ("touch", "R3"): 2,
    ("touch", "R4"): 3,
    ("touch", "L4"): 4,
    ("touch", "L3"): 5,
    ("touch", "L2"): 6,
    ("touch", "L1"): 7,
}

CONTROL_LABELS = {
    "song_back": "B MENU",
    "song_replay": "A AGAIN",
    "diagnostics_back": "B/L4 returns",
}
