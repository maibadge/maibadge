"""Shared MaiBadge configuration selected by ``MAIBADGE_VARIANT``."""

import os


VARIANT = os.getenv("MAIBADGE_VARIANT") or "bear_v1"
if VARIANT == "bear_v1":
    from boards import bear_v1 as profile
elif VARIANT == "machine_v2":
    from boards import machine_v2 as profile
else:
    raise ValueError("Unknown MAIBADGE_VARIANT: " + VARIANT)

UI_MODE = os.getenv("MAIBADGE_UI") or "display"
if UI_MODE not in ("display", "headless"):
    raise ValueError("Unknown MAIBADGE_UI: " + UI_MODE)

FIRMWARE_VERSION = "0.3.0-" + VARIANT
EXPECTED_CIRCUITPYTHON = "10.2.1"
EXPECTED_BOARD_ID = profile.EXPECTED_BOARD_ID

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
DISPLAY_BAUDRATE = 24_000_000
DISPLAY_CLOCK = profile.DISPLAY_CLOCK
DISPLAY_MOSI = profile.DISPLAY_MOSI
DISPLAY_DC = profile.DISPLAY_DC
DISPLAY_CS = profile.DISPLAY_CS
DISPLAY_RESET = profile.DISPLAY_RESET

PIXEL_PIN = profile.PIXEL_PIN
PIXEL_COUNT = 8
PIXEL_BRIGHTNESS = 0.25 if UI_MODE == "headless" else 1.0
ANIMATION_INTERVAL = 0.08

BUZZER_PIN = profile.BUZZER_PIN
BUZZER_DUTY = 24_000

BUTTON_PINS = profile.BUTTON_PINS
BUTTON_NAMES = profile.BUTTON_NAMES
BUTTON_ACTIVE_LOW = True

HAS_DISPLAY = UI_MODE == "display"
HAS_TOUCH = profile.HAS_TOUCH and HAS_DISPLAY
ENABLE_GIFS = profile.ENABLE_GIFS
ENABLE_GAME = profile.ENABLE_GAME
ENABLE_DIAGNOSTICS = profile.ENABLE_DIAGNOSTICS
STARTUP_STATUS = profile.STARTUP_STATUS
START_APP = profile.START_APP
TOUCH_CONFIG = profile.TOUCH_CONFIG
CONTROL_BINDINGS = profile.CONTROL_BINDINGS
CONTROL_LABELS = profile.CONTROL_LABELS
GAME_LANE_BINDINGS = profile.GAME_LANE_BINDINGS
TOUCH_SAMPLE_INTERVAL = 0.015
TOUCH_CALIBRATION_SAMPLES = 48
TOUCH_PRESS_MARGIN = 500
TOUCH_RELEASE_MARGIN = 250
TOUCH_STABLE_SAMPLES = 2

CONTROLLER_INTERVAL = 0.01

SPLASH_IMAGE = "/assets/splash/maibadge_festival.jpg"
SPLASH_MIN_SECONDS = 1.75
SPLASH_READY_SECONDS = 0.35

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

FACE_MEDIA = FACE_IMAGES + GIF_ASSETS if ENABLE_GIFS else FACE_IMAGES
MENU_BACKGROUND = "/assets/menu/menu_foreground.jpg"
MENU_BACKGROUND_EMPTY = "/assets/menu/menu_foreground_1.jpg"
MENU_ITEM_SELECTED = "/assets/menu/menu_item_indiv.jpg"
MENU_ITEM_SMALL = "/assets/menu/menu_item_indiv_small_62.jpg"
SONG_BACKGROUND = "/assets/menu/maisongchosen.jpg"

MENU_ITEMS = profile.PRIMARY_MENU_ITEMS + (
    ("led", "led"),
    ("buzzintro", "song_intro"),
    ("buzzeye", "song_eye"),
    ("buzzqz", "song_qzkago"),
    ("buzzmario", "song_mario"),
)
if ENABLE_GAME:
    MENU_ITEMS += (("game", "game"),)
if ENABLE_DIAGNOSTICS:
    MENU_ITEMS += (("diag", "diagnostics"),)
