"""MaiBadge no-display CircuitPython entry point."""

import sys
import traceback

import board

import config
from controller import Controller
from hardware import BadgeHardware


hardware = None

try:
    print(config.FIRMWARE_NAME, config.FIRMWARE_VERSION)
    print("CircuitPython", sys.implementation.version)
    print("Board", getattr(board, "board_id", "unknown"))
    hardware = BadgeHardware()
    Controller(hardware).run()
except Exception as error:
    try:
        traceback.print_exception(error)
    except TypeError:
        print("Fatal error:", error)
    if hardware is not None:
        hardware.safe_outputs()
    while True:
        pass
