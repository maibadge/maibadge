# MaiBadge bear: CircuitPython without a display

Minimal two-button firmware for CircuitPython 10.2.1 on the YD ESP32-S3 N16R8.
It does not initialize the display or capacitive-touch inputs.

## Install

Copy the contents of this directory to the root of `CIRCUITPY`.

## Controls

- Button A / GPIO9 cycles solid LED colours and animations.
- Button B / GPIO0 stops the current song and starts the next one.

Songs cycle through Mai Intro, Eye Song, QZKago, and Super Mario. The first
press starts Mai Intro. LED modes begin off and cycle through solid colours,
rainbow, chase, comet, and pulse.

GPIO0 is a boot-strapping pin. Do not hold button B while resetting or powering
the badge.

## Pin map

| Peripheral | GPIO |
|---|---:|
| LED-mode button | 9 |
| Song button | 0 |
| Eight NeoPixels | 15 |
| PWM buzzer | 47 |

## On-device smoke test

After copying the firmware, open the serial console and confirm the firmware
name and button instructions are printed. Press the LED button through all 12
modes and verify every LED and animation. Press the song button four times and
verify each complete song starts immediately; pressing it while a song is
playing must interrupt that song and start the next one. Finally, reset without
holding GPIO0 and confirm the LEDs start off and the buzzer stays silent.
