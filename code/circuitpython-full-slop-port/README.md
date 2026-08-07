# MaiBadge CircuitPython firmware

This is the canonical CircuitPython 10.2.1 firmware for the bear-shaped and
machine-shaped MaiBadge PCBs. Application, display, music, asset, and hardware
driver code is shared. `settings.toml` selects a small hardware profile.

See [MANUAL_UPLOAD.md](MANUAL_UPLOAD.md) for complete manual flashing and file
copy instructions.

## Select a PCB

Edit `settings.toml` before copying the firmware to `CIRCUITPY`:

```toml
MAIBADGE_VARIANT = "bear_v1"
```

Supported values:

| Variant | Buttons | Touch | LEDs | Buzzer |
|---|---|---|---:|---:|
| `bear_v1` | GPIO9 and GPIO0 | GPIO1–8 | GPIO15 | GPIO47 |
| `machine_v2` | GPIO21 and GPIO0 | None | GPIO42 | GPIO40 |

Both profiles use the GC9A01A display on SCK 14, MOSI 13, DC 10, CS 11, and
reset 12.

`bear_v1` is the default when `MAIBADGE_VARIANT` is absent. Unknown values stop
boot with an error instead of silently using the wrong GPIOs.

## Features

Shared features include:

- festival splash screen;
- a full-screen blue/red colour app using shades sampled from the reference artwork;
- static face gallery with persistent selection;
- animated GIF gallery on profiles that enable it;
- MaiMai-style menu and song screens;
- four non-blocking PWM songs;
- addressable LED colour modes;
- integrated diagnostics;
- the eight-lane rhythm game on the touch-enabled bear profile.

The machine profile enables GIFs for the verified YD ESP32-S3 N16R8 machine
badge. It disables the bear's eight-touch-lane game because the PCB has only
two usable controls. These are capability choices, not separate firmware
forks. Confirm the memory suffix before using this profile on another machine
badge.

## Controls

### Bear v1

- Boots into the face gallery; `color` is the second menu item.
- Colour app: R3/A next colour, L3 previous colour, L4/B menu.
- Gallery: R3/A next, L3 previous, L4/B menu.
- Menu: R3/A next, L3 previous, R4 select, B gallery.
- Songs: R4/A replay, L4/B menu.
- Rhythm game: eight touch lanes; B exits.

### Machine v2

- Boots directly into the colour app; `color` is the first menu item.
- Colour app: ADVANCE cycles blue/red, SELECT opens the menu.
- Gallery: ADVANCE next, SELECT menu.
- Menu: ADVANCE next, SELECT activate.
- Songs: ADVANCE replay, SELECT menu.
- Diagnostics: SELECT returns.

GPIO0 doubles as the boot-strapping input on both boards. Holding its button
during reset can enter the ESP32-S3 ROM bootloader.

## Architecture

- `boards/` contains pins, capabilities, control bindings, and labels.
- `config.py` selects a board profile and defines shared assets/timing.
- `controls.py` translates physical inputs into application actions.
- `hardware/` owns each physical peripheral exactly once.
- `apps/` contains gallery, menu, music, game, and diagnostics states.
- `assets/` and `lib/` are the deployable media and CircuitPython libraries.
- `tests/` contains host-side logic and profile checks.

Applications must use `controls.matches()` instead of checking GPIO-oriented
button or touch names directly. This keeps board differences out of the shared
UI and state machines.

## Physical validation

Host tests cannot verify display orientation, touch thresholds, LED order,
buzzer volume, or memory stability. After uploading a profile, run Diagnostics,
exercise every peripheral, and perform a mixed-use soak test. For `machine_v2`,
confirm the fitted ESP32-S3 memory suffix before selecting or flashing a
CircuitPython image.
