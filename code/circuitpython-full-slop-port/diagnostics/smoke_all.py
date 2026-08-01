"""Interactive all-peripheral smoke test.

Temporarily replace code.py with:
    import asyncio
    from diagnostics.smoke_all import run
    asyncio.run(run())
"""

import asyncio
import gc
import time

from hardware import BadgeHardware
from ui import colors


async def run():
    hardware = BadgeHardware()
    try:
        group = hardware.display.show_solid(colors.DARK_PURPLE)
        group.append(hardware.display.label("MaiBadge smoke test", 8, 24, colors.WHITE, 2))
        group.append(hardware.display.label("Watch serial output", 35, 60, colors.YELLOW))

        print("Calibrating: do not touch the electrodes")
        await hardware.calibrate()
        for row in hardware.touch.snapshot():
            print(row)

        for color in ((24, 0, 0), (0, 24, 0), (0, 0, 24), (0, 0, 0)):
            hardware.leds.set_all(color)
            await asyncio.sleep(0.4)

        for frequency in (262, 440, 659):
            hardware.buzzer.tone(frequency)
            await asyncio.sleep(0.18)
            hardware.buzzer.off()
            await asyncio.sleep(0.08)

        print("Press buttons/touch pads; reset to finish")
        next_report = 0.0
        while True:
            for event in hardware.poll_events():
                print(event)
            now = time.monotonic()
            if now >= next_report:
                next_report = now + 1.0
                print("heap", gc.mem_free(), hardware.touch.snapshot())
            await asyncio.sleep(0.015)
    finally:
        hardware.deinit()
