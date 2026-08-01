# MaiBadge MicroPython-to-CircuitPython Porting Plan

Status: implemented in this directory; physical-badge validation remains
Target firmware: CircuitPython 10.2.1
Target build: `yd_esp32_s3_n16r8`
Prepared: 2026-08-01

Implementation note: the source tree, selected assets, CircuitPython 10.x libraries, diagnostics, install guide, and host-side tests described by this plan have now been created beside this file. Host validation passes; the hardware-only acceptance items remain intentionally unchecked until the firmware is copied to a physical badge.

## 1. Goal and definition of done

Port the functional intent of `code/main` from MicroPython to CircuitPython while preserving the useful display, face gallery, menu, NeoPixel, buzzer/song, touch, button, and rhythm-game behavior. Use `code/circuitpython` as a hardware proof-of-concept, not as the architecture of the final port.

The port is done when the MaiBadge's ESP32-S3-WROOM-1-N16R8, running the tested YD ESP32-S3 N16R8 build of CircuitPython 10.2.1, can receive the contents of the port directory, cold boot without an exception, pass the hardware smoke tests, navigate every menu entry, enter and leave every app repeatedly, and run for at least 30 minutes without steadily losing heap or accumulating background tasks.

This plan deliberately does not require byte-for-byte or pixel-for-pixel preservation. MicroPython's immediate-mode `gc9a01` drawing API and CircuitPython's retained-mode `displayio` API are different. The target is equivalent behavior and appearance with a maintainable CircuitPython design.

## 2. Inputs reviewed

Primary inputs:

- `pcbs/bear/maibadge_bear_v1/maibadge_bear_v1.kicad_sch`
- `pcbs/bear/maibadge_bear_v1/maibadge_bear_v1.kicad_pcb`
- `code/main/boot.py`
- every Python module under `code/main/apps`, `code/main/hardware`, and `code/main/lib`
- all images and menu graphics under `code/main`
- the existing `code/circuitpython/code.py`, libraries, assets, `boot_out.txt`, and instructions

The bear v1 schematic/PCB is the hardware source of truth because it matches the display, NeoPixel, buzzer, and capacitive-touch pins used by the software. The older `pcbs/Justin/maibadge/maibadge_ver2` schematic was treated as historical corroboration, not as the target revision.

The existing CircuitPython directory is a useful proof that the display pinout and GC9A01 panel work, but it is not a complete port. Its `boot_out.txt` records CircuitPython 9.2.8, its code uses the old `displayio.FourWire` spelling, and it carries a 9.x-era library snapshot and approximately 6.28 MB of demo image/GIF assets. Those files should not be copied wholesale into the new port.

## 3. Verified CircuitPython 10.2.1 constraints

As of 2026-08-01, CircuitPython 10.2.1 is the latest stable release for the tested YD ESP32-S3 N16R8 build. The target module has 16 MB flash and 8 MB PSRAM. Hardware testing has confirmed that the `yd_esp32_s3_n16r8` build boots and works on the MaiBadge. The official build contains the modules needed here, including `_asyncio`, `bitmaptools`, `busio`, `digitalio`, `displayio`, `fourwire`, `gifio`, `jpegio`, `keypad`, `microcontroller`, `pwmio`, `touchio`, and the low-level NeoPixel support.

Compatibility rules for this port:

1. Flash exactly the tested `yd_esp32_s3_n16r8` 10.2.1 build. Do not use the no-PSRAM DevKitC N16 build or a build with a different flash/PSRAM configuration.
2. Use `fourwire.FourWire`; do not use the legacy `displayio.FourWire` call found in the current CircuitPython prototype.
3. Use the maintained `adafruit_gc9a01a.GC9A01A` display driver from the 10.x Adafruit bundle. Do not reuse the opaque `gc9a01.mpy` without identifying and testing its source/version.
4. Refresh all copied `.mpy` libraries from a CircuitPython 10.x bundle. The bytecode format is compatible between 9.x and 10.x, but a clean, recorded 10.x dependency set avoids stale APIs and shadowing.
5. Do not reuse the old `code/circuitpython/lib/asyncio` snapshot. Install the CircuitPython 10.x bundle's supported `asyncio` package together with its `adafruit_ticks` dependency; `_asyncio` is only the firmware helper and is not a replacement for the filesystem package.
6. Do not use `machine`, `Pin.irq`, `machine.Timer`, `_thread`, `time.ticks_ms`, `sleep_ms`, or CPU `freq()` calls. CircuitPython does not offer the MicroPython `machine` API, Python threads/interrupt callbacks are not the right application model, and monotonic time plus cooperative tasks replace the timer code.
7. Use the available PSRAM to reduce image and display-memory pressure, but still load assets deliberately and measure free heap. Multiple decoded GIFs or unnecessary full-screen framebuffers can still cause fragmentation or poor responsiveness.

Official references:

- [YD ESP32-S3 N16R8 board download and module list](https://circuitpython.org/board/yd_esp32_s3_n16r8/)
- [CircuitPython 10.2.1 release](https://github.com/adafruit/circuitpython/releases/tag/10.2.1)
- [CircuitPython 10.x library bundle](https://circuitpython.org/libraries)
- [`fourwire.FourWire` API](https://docs.circuitpython.org/en/10.2.1/shared-bindings/fourwire/)
- [`touchio.TouchIn` API](https://docs.circuitpython.org/en/10.2.1/shared-bindings/touchio/)
- [Maintained Adafruit GC9A01A driver](https://docs.circuitpython.org/projects/gc9a01a/en/latest/)

## 4. Hardware source-of-truth pin map

Use one `config.py` pin map and import it everywhere. Do not repeat pin literals in apps.

| Function | Schematic net | ESP32-S3 GPIO | CircuitPython object | Notes |
|---|---|---:|---|---|
| TFT clock | `OLED_SCL` | 14 | `board.GPIO14` / `busio.SPI` | GC9A01 SPI clock |
| TFT data | `OLED_SDA` | 13 | `board.GPIO13` / `busio.SPI` MOSI | Display is write-only; no MISO required |
| TFT data/command | `OLED_DC` | 10 | `board.GPIO10` | Pass to `FourWire(command=...)` |
| TFT chip select | `OLED_CS` | 11 | `board.GPIO11` | Pass to `FourWire(chip_select=...)` |
| TFT reset | `OLED_RST` | 12 | `board.GPIO12` | Pass to `FourWire(reset=...)` |
| Eight RGB LEDs | `main led DIN` | 15 | `board.GPIO15` | Eight chained addressable pixels |
| Buzzer | `buzzer` | 47 | `board.GPIO47` | `pwmio.PWMOut(variable_frequency=True)` |
| User button A | `button 1` | 9 | `board.GPIO9` | Active level and pull must be confirmed on hardware |
| Boot/button B | `GPIO0_BOOT` | 0 | `board.GPIO0` | Active low; holding during reset enters bootloader |
| Touch R1 | `touch_sensor_1` | 1 | `board.GPIO1` | `touchio.TouchIn` |
| Touch L1 | `touch_sensor_2` | 2 | `board.GPIO2` | `touchio.TouchIn` |
| Touch L3 | `touch_sensor_3` | 3 | `board.GPIO3` | `touchio.TouchIn` |
| Touch R3 | `touch_sensor_4` | 4 | `board.GPIO4` | `touchio.TouchIn` |
| Touch R2 | `touch_sensor_5` | 5 | `board.GPIO5` | `touchio.TouchIn` |
| Touch R4 | `touch_sensor_6` | 6 | `board.GPIO6` | `touchio.TouchIn` |
| Touch L4 | `touch_sensor_7` | 7 | `board.GPIO7` | `touchio.TouchIn` |
| Touch L2 | `touch_sensor_8` | 8 | `board.GPIO8` | `touchio.TouchIn` |
| Native USB D- | `USB_D-` | 19 | reserved | Do not allocate in application code |
| Native USB D+ | `USB_D+` | 20 | reserved | Do not allocate in application code |

Important discrepancy: `code/main/hardware/buttons.py` declares button A on GPIO21, but the bear v1 PCB routes `button 1` to GPIO9 and leaves GPIO21 unconnected. The port should default to GPIO9. Phase 1 must prove this on a physical badge before higher-level app work. If a manufactured revision really uses GPIO21, add an explicit board-revision setting instead of silently changing the common map.

The touch name mapping above preserves `code/main/hardware/touchpads.py`. It is intentionally non-sequential around the face.

## 5. Runtime/API conversion matrix

| MicroPython mechanism | CircuitPython 10.2.1 replacement | Porting action |
|---|---|---|
| `machine.Pin` | `board` plus `digitalio`, `keypad`, or peripheral object | Centralize ownership; deinit cleanly |
| `Pin.irq()` | `keypad.Keys` event queue or async polling | Deliver button events in task context, never an IRQ callback |
| `machine.Timer` periodic callbacks | long-lived `asyncio` tasks using `await asyncio.sleep()` | Controller owns and cancels tasks on app exit |
| `time.ticks_ms()` | `time.monotonic_ns()` or `time.monotonic()` | Use wrap-safe elapsed-time helpers and edge debouncing |
| `time.sleep_ms()` / `asyncio.sleep_ms()` | seconds with `time.sleep()` / `await asyncio.sleep()` | Convert milliseconds to seconds explicitly |
| `_thread` | `asyncio.create_task()` | Songs and UI cooperate on one interpreter thread |
| `machine.PWM` | `pwmio.PWMOut` | Set `frequency`, then `duty_cycle`; use zero duty for silence |
| MicroPython `neopixel.write()` | CircuitPython `neopixel.NeoPixel(..., auto_write=False).show()` | Preserve eight-pixel and brightness behavior |
| `TouchPad.read()` | `touchio.TouchIn.raw_value` | Calibrate thresholds after startup and expose `.value`/edge events |
| `TouchPad` threshold globals | per-pad baseline plus margin | Sample multiple readings; allow diagnostics and future persistence |
| immediate `tft.fill/circle/line/text` | `displayio`, `vectorio`, `bitmaptools`, and labels | Rebuild screens as groups and update object properties |
| `tft.jpg(path, x, y)` | `jpegio` or a tested image loader into one TileGrid | Release the previous bitmap/group before loading the next asset |
| custom Python VGA font modules | `terminalio.FONT` and/or bundled BDF/PCF fonts | Use scale 1 for 8x16-like text and scale 2 for 16x32-like text |
| `gc9a01.BLACK`, etc. | project RGB constants | Remove dependency on driver-specific color names |
| `gc.enable()` | no direct equivalent needed | Use `gc.collect()` at screen transitions and inspect `gc.mem_free()` |
| `freq(160_000_000)` | no application setting | Accept firmware CPU configuration |
| `microcontroller.nvm[0]` | same API, with validation and modulo | Optional persisted app/image index; protect against erased/out-of-range values |

## 6. Proposed target layout

After implementation, keep this plan and build the port beside it:

```text
circuitpython-full-slop-port/
├── PORTING_PLAN.md
├── README.md
├── code.py
├── config.py
├── lib/
│   ├── adafruit_gc9a01a.mpy
│   ├── neopixel.mpy
│   ├── asyncio/
│   ├── adafruit_ticks.mpy
│   └── only the recorded transitive dependencies actually required
├── hardware/
│   ├── __init__.py
│   ├── badge.py
│   ├── buttons.py
│   ├── buzzer.py
│   ├── display.py
│   ├── leds.py
│   └── touch.py
├── ui/
│   ├── assets.py
│   ├── colors.py
│   └── widgets.py
├── apps/
│   ├── base.py
│   ├── controller.py
│   ├── face.py
│   ├── game.py
│   ├── menu.py
│   └── songs.py
├── assets/
│   ├── faces/
│   └── menu/
├── diagnostics/
│   ├── smoke_all.py
│   ├── test_buttons.py
│   ├── test_buzzer.py
│   ├── test_display.py
│   ├── test_leds.py
│   └── test_touch.py
└── LIBRARIES.md
```

`code.py` should do little beyond constructing one `BadgeHardware`, constructing the controller, and calling `asyncio.run(controller.run())`. `boot.py` is unnecessary unless USB/storage behavior must be configured before the CircuitPython workflow starts.

## 7. Architecture and lifecycle

### 7.1 Hardware ownership

Create every pin/peripheral once in `BadgeHardware`. Apps receive references to stable service objects; they never construct a second `TouchIn`, `PWMOut`, SPI bus, display bus, or NeoPixel object for the same pins.

Each service exposes intent rather than raw APIs where useful:

- `buttons.events()` yields debounced press/release events with logical names.
- `touch.events()` yields edge events and also exposes raw readings for diagnostics.
- `buzzer.play_tone()` and an async song player own PWM timing.
- `display.show(group)` and the asset manager replace the root group safely.
- `leds.fill()`/`show()` own brightness and pixel writes.

### 7.2 Single app controller

Replace nested `load()` callbacks and Timer creation with a single state machine:

```text
BOOT -> FACE -> MENU -> selected app -> MENU
```

Only the controller changes apps. An app implements async `enter()`, `run()`, and `exit()` (or one async context-managed `run()`). The controller cancels and awaits all app-owned tasks before entering the next app. This prevents the existing failure mode where repeated `load()` calls create additional timers or handlers.

### 7.3 Event model

Use cooperative tasks with bounded polling:

- button task: `keypad.Keys` event queue, approximately 20 ms scan/debounce
- touch task: poll all eight pads around 50-100 Hz, with per-pad hysteresis and edge detection
- app/UI task: waits on a small event queue and updates only changed display objects
- music task: awaits note and gap durations; can be cancelled immediately
- game task: uses monotonic deadlines rather than counting Timer callbacks

Never redraw a JPEG, rebuild a full display group, or call a blocking song loop from an input callback.

### 7.4 Display and memory model

Initialize the display with:

- `displayio.release_displays()`
- `busio.SPI(clock=board.GPIO14, MOSI=board.GPIO13)`
- `fourwire.FourWire(... IO10, IO11, IO12 ...)`
- `adafruit_gc9a01a.GC9A01A(..., width=240, height=240)`

Start with a conservative documented bus baudrate and raise it only after a display soak test. The MicroPython code used 40 MHz, but that is not by itself proof that the CircuitPython driver, panel, and PCB are stable at the same setting.

Use one root group per screen. For the face gallery, remove references to the previous bitmap and TileGrid, swap the root group, call `gc.collect()`, and record free heap before and after 100 image changes. For the menu, keep static background and selection TileGrids cached only if heap measurements justify it. For the rhythm game, prefer a fixed set of reusable `vectorio.Circle`/label objects over allocating objects on every frame.

## 8. Phased implementation plan

### Phase 0 - freeze the baseline

- Record the exact badge PCB revision and photograph/label the manufactured board used for testing.
- Archive serial output from the working MicroPython firmware and the existing CircuitPython display prototype.
- Capture expected behavior for face navigation, menu ordering, LED colors, songs, touch layout, and game timing.
- Hash or otherwise inventory source images so conversion does not silently replace artwork.
- Decide whether the boot button on GPIO0 is an intended normal UI input. If so, document that it must not be held during reset.

Exit gate: expected behavior and the physical revision are unambiguous.

### Phase 1 - firmware, dependency, and pin smoke tests

- Flash CircuitPython 10.2.1 for `yd_esp32_s3_n16r8`.
- Confirm `boot_out.txt` reports both version `10.2.1` and the exact board ID.
- Create the target skeleton, `config.py`, `README.md`, and recorded dependency list.
- Install only 10.x-compatible libraries, led by `adafruit_gc9a01a` and `neopixel`.
- Implement one diagnostic per peripheral before building shared abstractions.
- Verify GPIO9 is the actual user button, GPIO0 is the second/boot button, and both active levels/pull arrangements.
- Print all touch raw values untouched/touched for at least 10 seconds and derive initial threshold margins.

Exit gate: display color test, all eight touch pads, both buttons, all eight LEDs, and buzzer pass independently after cold boot and soft reload.

### Phase 2 - CircuitPython hardware layer

- Implement stable, single-owner services for display, input, touch, LEDs, and buzzer.
- Add `deinit()` for diagnostics and controlled shutdown, even though production owns peripherals for the process lifetime.
- Add a diagnostics screen/serial report showing raw touch values, thresholds, button states, heap, and firmware version.
- Add automated touch baseline calibration using multiple samples, a margin, and hysteresis. Do not transplant the MicroPython fixed 30000/40000 thresholds without measurement.
- Make buzzer duty configurable and start conservatively to avoid excessive volume/current.

Exit gate: `diagnostics/smoke_all.py` runs every device concurrently without pin-in-use errors or missed input.

### Phase 3 - controller, input events, and screen primitives

- Implement the single app controller and transition contract.
- Implement button and touch events with press, release, and debounce/hysteresis.
- Build reusable black-screen, image-screen, label, ring, and menu-selection helpers.
- Add a task registry so the controller can cancel and await every task on transition.
- Add an error screen that prints the exception to serial and offers a safe reset/menu action where possible.

Exit gate: a dummy app can be entered/exited 100 times without duplicate events, pin allocation failures, live-task growth, or meaningful heap drift.

### Phase 4 - face gallery

- Copy only the face images referenced by `maiface.py`; do not copy unrelated 6 MB GIF demos from the prototype.
- Normalize names and paths under `/assets/faces` and validate every file is 240 x 240 and decodable.
- Port forward/back navigation to R3/L3 and preserve the button shortcut if desired.
- Use edge events so holding a touch pad changes one image rather than racing through the list.
- Make L4 return to menu through the controller.
- Optionally persist the selected face index in NVM with bounds checking and modulo.

Exit gate: cycle forward and backward through the entire gallery 100 times with no exception and stable heap.

### Phase 5 - menu, LEDs, and songs

- Port the menu using retained display objects rather than repeatedly decoding all menu JPEGs.
- Preserve menu order: face, LED mode, intro, eye, QZKago, Mario, game; use friendly labels rather than four-character truncation where space allows.
- Port LED colors with `auto_write=False`, `.show()`, and a safe default brightness.
- Port RTTTL parsing as ordinary Python, but replace `_thread` and the un-awaited coroutine in `MusicPlayer.play_music()` with one cancellable async song task.
- Ensure note durations use seconds consistently and rests always set PWM duty to zero.
- Stop any active song on app exit and silence the buzzer in `finally`.

Exit gate: rapidly switch songs/apps 50 times; no overlapping songs remain and buzzer is always silent after exit.

### Phase 6 - rhythm game

- Treat `maigame.py` as the behavioral prototype and `maigame_2.py` as incomplete experimental code; merge only intentional features.
- Fix source defects during the port instead of emulating them:
  - `maigame.py` refers to undefined `delta`; use the intended sensor-offset table.
  - `maigame_2.py` uses `range(self.chart)` instead of its length.
  - combo updates must use `self.combo`.
  - list removal during indexed iteration must be replaced with explicit object states or filtered collections.
  - the current menu never actually instantiates the game because that code is commented out.
- Represent chart timing as absolute monotonic hit deadlines.
- Separate update, input judging, and drawing. Reuse note objects and update positions at a fixed target cadence.
- Define judgement windows explicitly (for example perfect/good/miss) and test boundary values without hardware.
- Use touch press edges, not continuously true levels, for hits.
- Always provide a reliable exit gesture and cancel all game/music tasks on exit.

Exit gate: a deterministic test chart produces expected judgements; a five-minute play test maintains cadence and exits cleanly.

### Phase 7 - asset, storage, and compatibility hardening

- Remove duplicate `menu_graphics` trees and unused demo assets from the deliverable.
- Prefer JPEG/BMP assets supported by the chosen loader; GIF support is optional and must not be required by the main-code port.
- Record every filesystem library name, version, bundle date, and source in `LIBRARIES.md`.
- Verify the deliverable fits on the actual CIRCUITPY partition with at least 15% free space for safe edits and future assets.
- Run a cold-boot test, soft-reload test, USB reconnect test, and 30-minute soak test on CircuitPython 10.2.1.
- Run a static host check over all `.py` files and a device import smoke test over every module.
- Write install, recovery, serial-console, and known GPIO0 boot-button behavior in `README.md`.

Exit gate: a clean-board installation following only `README.md` passes the complete acceptance checklist.

## 9. Acceptance checklist

Firmware and installation:

- [ ] `boot_out.txt` says CircuitPython 10.2.1 and `yd_esp32_s3_n16r8`.
- [ ] Startup diagnostics confirm that PSRAM is enabled and the expected additional heap is available.
- [ ] A clean install requires no file from the old `code/circuitpython/lib/asyncio` directory.
- [ ] Every filesystem `.mpy` dependency is from the recorded compatible bundle/version.
- [ ] At least 15% of CIRCUITPY remains free.

Hardware:

- [ ] GC9A01 initializes after cold boot and Ctrl-D soft reload with no pin-in-use error.
- [ ] Red, green, blue, white, and black display tests are correct and stable.
- [ ] GPIO9 button and GPIO0 boot/button generate exactly one press and one release event.
- [ ] Each logical touch name matches its physical pad and can be pressed independently.
- [ ] Touch idle readings do not self-trigger during a 10-minute idle test.
- [ ] All eight NeoPixels address in the correct order at safe brightness.
- [ ] Buzzer plays at least three reference frequencies and silences on cancellation/error.

Apps and lifecycle:

- [ ] Face gallery visits every asset forward and backward and exits through L4.
- [ ] Menu wraps in both directions and launches every entry.
- [ ] LED entry advances modes without blocking input.
- [ ] Each song starts once, can be interrupted, and never overlaps a previous song.
- [ ] Game judges a deterministic chart correctly and returns to menu.
- [ ] One hundred app transitions do not grow the number of live tasks.
- [ ] Free heap after one hundred face changes/app transitions returns near the post-boot baseline after GC.
- [ ] Thirty-minute mixed-use soak has no crash, watchdog reset, display corruption, or stuck tone.

## 10. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Manufactured PCB differs from bear v1 files | Wrong button or peripheral pin | Make physical pin smoke tests the first gate; support explicit revision maps if proven necessary |
| PSRAM is present but display/image workloads still fragment memory | Degrading performance or allocation failures after repeated transitions | Reuse game objects, release obsolete groups/bitmaps, run transition soak tests, and measure heap rather than assuming PSRAM removes all limits |
| Stale opaque `.mpy` libraries | Import errors or old display API | Replace with recorded 10.x bundle libraries and maintained `adafruit_gc9a01a` |
| GPIO0 doubles as boot strap | Badge enters bootloader if held at reset | Document behavior; avoid using it for a required hold gesture |
| Touch readings vary by enclosure/person/power | False or missed touches | Multi-sample calibration, margin, hysteresis, diagnostics, optional persisted calibration |
| Timer/IRQ logic is ported literally | Reentrancy, allocation, and UI freezes | Use one cooperative event loop and controller-owned tasks |
| Display updates or JPEG decode block input | Poor menu/game response | Decode only at transitions, reuse display objects, measure frame/update time |
| Existing game code contains logic defects | Port appears unstable even when APIs are correct | Define behavior with deterministic tests and repair listed defects during conversion |
| Asset paths diverge between source trees | Missing images at runtime | Build one asset manifest and validate dimensions/existence on host before copying |

## 11. Recommended execution order

Implement in this strict order:

1. exact firmware and pin smoke tests;
2. display/touch/button/LED/buzzer services;
3. controller and lifecycle stress test;
4. face gallery;
5. menu and LEDs;
6. async songs;
7. rhythm game;
8. storage cleanup, dependency lock, soak test, and documentation.

Do not begin by mechanically translating all source files. The highest-risk unknowns are the physical button revision, touch calibration, retained-mode display behavior and fragmentation, and task lifecycle. Resolving those first prevents app-level work from being built on the wrong assumptions.
