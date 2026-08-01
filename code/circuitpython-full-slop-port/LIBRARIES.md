# Bundled CircuitPython libraries

All files in `lib/` were selected from the official Adafruit CircuitPython Bundle:

- Bundle release: `20260729`
- Archive: `adafruit-circuitpython-bundle-10.x-mpy-20260729.zip`
- Release page: <https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/tag/20260729>
- Target runtime: CircuitPython 10.2.1

Included direct dependencies:

- `adafruit_gc9a01a.mpy` 1.0.3 — maintained GC9A01A `displayio` driver
- `neopixel.mpy` 6.4.2 — eight addressable RGB LEDs
- `adafruit_display_text/` 5.0.5 — bitmap labels
- `adafruit_imageload/` 1.24.8 — source JPEG decoding into `displayio` objects
- `asyncio/` 3.1.1 — cooperative controller runtime

Included transitive dependencies:

- `adafruit_pixelbuf.mpy` 2.0.12
- `adafruit_ticks.mpy` 1.1.7
- `adafruit_bitmap_font/` 2.4.2

Do not replace these with the older libraries from `code/circuitpython`. To update them, select the equivalent files from a current CircuitPython **10.x** bundle and repeat all on-device smoke and soak tests.
