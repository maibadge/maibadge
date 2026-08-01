"""Low-level GC9A01 panel probe using the known-working MaiBadge init."""

import struct
import time

import busio
import displayio
from fourwire import FourWire

import config


INIT = (
    (0xEF, b""),
    (0xEB, b"\x14"),
    (0xFE, b""),
    (0xEF, b""),
    (0xEB, b"\x14"),
    (0x84, b"\x40"),
    (0x85, b"\xFF"),
    (0x86, b"\xFF"),
    (0x87, b"\xFF"),
    (0x88, b"\x0A"),
    (0x89, b"\x21"),
    (0x8A, b"\x00"),
    (0x8B, b"\x80"),
    (0x8C, b"\x01"),
    (0x8D, b"\x01"),
    (0x8E, b"\xFF"),
    (0x8F, b"\xFF"),
    (0xB6, b"\x00\x00"),
    (0x3A, b"\x55"),
    (0x90, b"\x08\x08\x08\x08"),
    (0xBD, b"\x06"),
    (0xBC, b"\x00"),
    (0xFF, b"\x60\x01\x04"),
    (0xC3, b"\x13"),
    (0xC4, b"\x13"),
    (0xC9, b"\x22"),
    (0xBE, b"\x11"),
    (0xE1, b"\x10\x0E"),
    (0xDF, b"\x21\x0C\x02"),
    (0xF0, b"\x45\x09\x08\x08\x26\x2A"),
    (0xF1, b"\x43\x70\x72\x36\x37\x6F"),
    (0xF2, b"\x45\x09\x08\x08\x26\x2A"),
    (0xF3, b"\x43\x70\x72\x36\x37\x6F"),
    (0xED, b"\x1B\x0B"),
    (0xAE, b"\x77"),
    (0xCD, b"\x63"),
    (0x70, b"\x07\x07\x04\x0E\x0F\x09\x07\x08\x03"),
    (0xE8, b"\x34"),
    (0x62, b"\x18\x0D\x71\xED\x70\x70\x18\x0F\x71\xEF\x70\x70"),
    (0x63, b"\x18\x11\x71\xF1\x70\x70\x18\x13\x71\xF3\x70\x70"),
    (0x64, b"\x28\x29\xF1\x01\xF1\x00\x07"),
    (0x66, b"\x3C\x00\xCD\x67\x45\x45\x10\x00\x00\x00"),
    (0x67, b"\x00\x3C\x00\x00\x00\x01\x54\x10\x32\x98"),
    (0x74, b"\x10\x85\x80\x00\x00\x4E\x00"),
    (0x98, b"\x3E\x07"),
    (0x35, b""),
    (0x21, b""),
    (0x11, b""),
)


def run():
    displayio.release_displays()
    spi = busio.SPI(clock=config.DISPLAY_CLOCK, MOSI=config.DISPLAY_MOSI)
    bus = FourWire(
        spi,
        command=config.DISPLAY_DC,
        chip_select=config.DISPLAY_CS,
        reset=config.DISPLAY_RESET,
        baudrate=10_000_000,
    )
    for command, data in INIT:
        bus.send(command, data)
    time.sleep(0.12)
    bus.send(0x29, b"")
    time.sleep(0.02)
    bus.send(0x2A, struct.pack(">HH", 0, 239))
    bus.send(0x2B, struct.pack(">HH", 0, 239))
    bus.send(0x2C, b"\xF8\x00" * (240 * 240))
    print("GC9A01 raw probe: red frame sent")
    return spi, bus
