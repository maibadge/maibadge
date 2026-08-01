# MaiBadge CircuitPython firmware

This is the working CircuitPython port of the original `code/main` MicroPython firmware.

## Required firmware

- CircuitPython: **10.2.1**
- Download target: **YD ESP32-S3 N16R8**
- Board ID expected by this project: `yd_esp32_s3_n16r8`
- Memory configuration: 16 MB flash and 8 MB PSRAM

Download the firmware from:

<https://circuitpython.org/board/yd_esp32_s3_n16r8/>

The YD N16R8 build has been tested on the MaiBadge hardware. Do not substitute the no-PSRAM `espressif_esp32s3_devkitc_1_n16` build.

## Install

1. Back up any files currently on `CIRCUITPY`.
2. Flash CircuitPython 10.2.1 for `yd_esp32_s3_n16r8`.
3. Copy the **contents** of this directory to the root of `CIRCUITPY`.
4. Wait for automatic reload, then open the serial console.
5. During the `Calibrating touch...` screen, keep fingers and conductive objects away from all eight touch electrodes.
6. Confirm the serial log lists a baseline and threshold for every pad.

The included `lib` directory is intentionally self-contained and comes from the official CircuitPython 10.x bundle dated 2026-07-29.

## Controls

Face gallery:

- R3 or button A: next image
- L3: previous image
- L4 or button B: open the menu

Menu:

- R3 or button A: next item
- L3: previous item
- R4: select
- button B: return to the face gallery

Songs:

- R4 or button A: restart
- L4 or button B: return to menu

Rhythm game:

- Touch the physical electrode reached by each moving yellow note.
- Button B returns to the menu.

Diagnostics:

- Shows raw touch values, calibrated baselines, touch states, and free heap.
- L4 or button B returns to the menu.

## Capacitive touch

The PCB uses the ESP32-S3's built-in capacitive-touch peripheral. There is no external touch controller.

| Pad | GPIO | Pad | GPIO |
|---|---:|---|---:|
| R1 | 1 | L1 | 2 |
| L3 | 3 | R3 | 4 |
| R2 | 5 | R4 | 6 |
| L4 | 7 | L2 | 8 |

At every boot, the firmware averages 48 untouched samples independently for each electrode. A press uses `baseline + TOUCH_PRESS_MARGIN`; release uses the lower `baseline + TOUCH_RELEASE_MARGIN`. Two consecutive samples are required before an edge event is emitted. Untouched baselines then track slow environmental drift.

If touch is too sensitive or insensitive, edit these values in `config.py`:

```python
TOUCH_PRESS_MARGIN = 500
TOUCH_RELEASE_MARGIN = 250
TOUCH_STABLE_SAMPLES = 2
```

Use the Diagnostics app to observe real values before changing them. Keep the press margin greater than the release margin.

## Hardware mapping

| Peripheral | GPIO(s) |
|---|---|
| GC9A01A TFT | SCK 14, MOSI 13, DC 10, CS 11, reset 12 |
| Eight NeoPixels | 15 |
| PWM buzzer | 47 |
| Button A | 9 |
| Boot/button B | 0 |
| Capacitive touch | 1 through 8 |

GPIO0 is also a boot-strapping pin. Holding button B while resetting the badge can enter the ROM bootloader; this is normal.

## Diagnostics smoke test

The integrated Diagnostics menu is the easiest input test. For a longer all-peripheral smoke test, temporarily replace `code.py` with:

```python
import asyncio
from diagnostics.smoke_all import run

asyncio.run(run())
```

The test calibrates touch, cycles the LEDs, plays three short tones, and continuously prints button/touch events and heap measurements.

Restore the supplied `code.py` afterward.

## Architecture

- `code.py` starts one cooperative controller.
- `hardware/` owns each physical peripheral exactly once.
- `apps/` contains face, menu, songs, diagnostics, and the rhythm game.
- `ui/` contains display helpers and colours.
- `assets/` contains only artwork used by the port.
- `lib/` contains the recorded CircuitPython 10.x dependencies.

The rhythm game repairs defects in the original experimental implementation: it uses monotonic hit deadlines, does not mutate lists while indexing them, emits one hit per touch edge, and can always exit with button B.

## First-device verification still required

Host checks can validate Python syntax and pure logic, but these checks require the physical badge:

- display orientation and stable 40 MHz SPI operation;
- GPIO9 button active level and pull configuration;
- touch margins under USB and battery power;
- NeoPixel colour order and physical order;
- acceptable buzzer volume/duty cycle;
- repeated image changes and app transitions without unacceptable heap fragmentation;
- 30-minute mixed-use soak test.

If the display is unstable, reduce `DISPLAY_BAUDRATE` in `config.py` to `24_000_000` before investigating other causes.
