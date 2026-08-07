"""MaiBadge CircuitPython 10.2.1 entry point."""

import asyncio
import gc
import sys
import traceback

import board

import config
from apps.controller import Controller
from hardware import BadgeHardware


hardware = None


async def main():
    global hardware
    print("MaiBadge firmware", config.FIRMWARE_VERSION)
    print("MaiBadge variant", config.VARIANT)
    print("CircuitPython", sys.implementation.version)
    print("Board", getattr(board, "board_id", "unknown"))
    print("Initial free heap", gc.mem_free())
    hardware = BadgeHardware()
    controller = Controller(hardware)
    await controller.run()


try:
    asyncio.run(main())
except Exception as error:  # CircuitPython needs an on-device failure screen.
    try:
        traceback.print_exception(error)
    except TypeError:
        print("Fatal error:", error)
    if hardware is not None:
        hardware.safe_outputs()
        hardware.display.show_error(error)
    while True:
        pass
