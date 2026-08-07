# No-display firmware moved

The no-display implementation is now part of the canonical firmware in
[`../circuitpython-full-slop-port`](../circuitpython-full-slop-port).

Select the PCB and enable headless mode in its `settings.toml`:

```toml
MAIBADGE_VARIANT = "bear_v1"
MAIBADGE_UI = "headless"
```

For the machine PCB, use `machine_v2` instead. In headless mode the display
and touch hardware are not imported or initialized. The first button cycles
the twelve LED modes; the second interrupts the current song and starts the
next song.

See the canonical firmware's `MANUAL_UPLOAD.md` for installation instructions.
