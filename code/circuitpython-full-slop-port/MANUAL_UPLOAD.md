# Manual CircuitPython installation

This directory is the canonical firmware for both supported MaiBadge PCBs.
Select the target in `settings.toml` before uploading:

```toml
MAIBADGE_VARIANT = "bear_v1"
```

or:

```toml
MAIBADGE_VARIANT = "machine_v2"
```

## Update an existing CircuitPython installation

1. Connect the badge with a USB data cable and wait for the `CIRCUITPY` drive.
2. Back up any files on `CIRCUITPY` that you want to keep.
3. Edit this directory's `settings.toml` to select the correct PCB.
4. Copy `code.py`, `config.py`, `controls.py`, and `settings.toml` to the root
   of `CIRCUITPY`, replacing older copies.
5. Copy `apps`, `assets`, `boards`, `diagnostics`, `hardware`, `lib`, and `ui`
   to the root of `CIRCUITPY`, replacing their older contents.
6. Safely eject `CIRCUITPY`. CircuitPython normally reloads automatically;
   otherwise press RESET once.
7. Open a serial console and confirm that `MaiBadge variant` reports the
   profile selected in `settings.toml`.

Do not merge new folders over an unknown older installation indefinitely.
Stale Python or library files can remain loadable. When changing variants,
delete the listed application directories from `CIRCUITPY` before copying
their replacements.

The `machine_v2` profile enables GIF playback for the verified N16R8 machine
badge. `assets/splash/maibadge_festival_source.png` is an editable source file
and may be omitted from any device upload.

## Fresh CircuitPython installation on ESP32-S3

Flashing erases the device. Back up the current `CIRCUITPY` contents first.

The bear PCB is tested with CircuitPython 10.2.1 for the YD ESP32-S3 N16R8.
The machine PCB schematic says `ESP32-S3-WROOM-1` but does not record its
flash/PSRAM suffix. Confirm the fitted module marking and download a
CircuitPython `.bin` whose flash and PSRAM layout matches it. Do not assume
N16R8 solely because the code supports that build.

1. Install Espressif's flashing utility:

   ```powershell
   py -m pip install --upgrade esptool
   ```

2. Download the matching CircuitPython 10.2.1 `.bin` file.
3. Enter the ESP32-S3 ROM bootloader: hold GPIO0/BOOT, press and release RESET,
   then release BOOT. On the machine PCB, GPIO0 is SELECT.
4. Find the new COM port in Windows Device Manager.
5. Erase and flash, replacing `COM7` and the image path:

   ```powershell
   py -m esptool --chip esp32s3 --port COM7 erase-flash
   py -m esptool --chip esp32s3 --port COM7 --after hard-reset write-flash --compress 0x0 .\circuitpython.bin
   ```

6. Wait for `CIRCUITPY` and follow the application upload procedure above.

## Machine-PCB controls

| Screen | ADVANCE (GPIO21) | SELECT (GPIO0) |
|---|---|---|
| Gallery | Next item | Open menu |
| Menu | Next item | Activate item |
| LED item | Next menu item | Cycle colour |
| Song | Replay | Return to menu |
| Diagnostics | Record event | Return to menu |

GPIO0 is a boot-strapping pin. Do not hold SELECT while powering or resetting
the badge unless you intend to enter the ROM bootloader.

## Quick verification

After uploading, check the serial console and verify the display, both buttons,
all eight LEDs, and the buzzer. The Diagnostics menu shows the active profile,
input events, and free heap. For the machine PCB, also confirm that the LEDs
are on GPIO42 and the buzzer is on GPIO40.
