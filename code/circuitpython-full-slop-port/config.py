"""MaiBadge hardware and application configuration."""

import board

FIRMWARE_VERSION = "0.1.0"
EXPECTED_CIRCUITPYTHON = "10.2.1"
EXPECTED_BOARD_ID = "yd_esp32_s3_n16r8"

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
DISPLAY_BAUDRATE = 24_000_000
DISPLAY_CLOCK = board.GPIO14
DISPLAY_MOSI = board.GPIO13
DISPLAY_DC = board.GPIO10
DISPLAY_CS = board.GPIO11
DISPLAY_RESET = board.GPIO12

PIXEL_PIN = board.GPIO15
PIXEL_COUNT = 8
PIXEL_BRIGHTNESS = 1.0

BUZZER_PIN = board.GPIO47
BUZZER_DUTY = 24_000

BUTTON_PINS = (board.GPIO9, board.GPIO0)
BUTTON_NAMES = ("A", "B")
BUTTON_ACTIVE_LOW = True

# Preserve the physical naming used by the original MicroPython firmware.
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
TOUCH_SAMPLE_INTERVAL = 0.015
TOUCH_CALIBRATION_SAMPLES = 48
TOUCH_PRESS_MARGIN = 500
TOUCH_RELEASE_MARGIN = 250
TOUCH_STABLE_SAMPLES = 2

CONTROLLER_INTERVAL = 0.01

FACE_IMAGES = (
    "/assets/faces/maibear1.jpg",
    "/assets/faces/maibear_study_atb.jpg",
    "/assets/faces/maibear_og.jpg",
    "/assets/faces/maibear_clown.jpg",
    "/assets/faces/maibear2.jpg",
    "/assets/faces/maibear_study_work_harder.jpg",
    "/assets/faces/maibear_study_water_thing.jpg",
    "/assets/faces/menu_foreground_1.jpg",
    "/assets/faces/maisongselect.jpg",
    "/assets/faces/maisongchosen.jpg",
    "/assets/faces/maigameplay1.jpg",
    "/assets/faces/maigameplay2.jpg",
)

GIF_ASSETS = (
    "/assets/gifs/ezgif-7-562f90826a.gif",
    "/assets/gifs/greycat-faces_style_2.gif",
    "/assets/gifs/greymecha.gif",
    "/assets/gifs/maislides.gif",
    "/assets/gifs/nyan-cat-kawaii.gif",
)

FACE_MEDIA = FACE_IMAGES + GIF_ASSETS
MENU_BACKGROUND = "/assets/menu/menu_foreground.jpg"
MENU_BACKGROUND_EMPTY = "/assets/menu/menu_foreground_1.jpg"
MENU_ITEM_SELECTED = "/assets/menu/menu_item_indiv.jpg"
MENU_ITEM_SMALL = "/assets/menu/menu_item_indiv_small_62.jpg"
SONG_BACKGROUND = "/assets/menu/maisongchosen.jpg"

MENU_ITEMS = (
    ("face", "face"),
    ("led", "led"),
    ("buzzintro", "song_intro"),
    ("buzzeye", "song_eye"),
    ("buzzqz", "song_qzkago"),
    ("buzzmario", "song_mario"),
    ("game", "game"),
)
