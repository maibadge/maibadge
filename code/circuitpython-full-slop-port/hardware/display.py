"""GC9A01A display ownership and retained-mode UI helpers."""

import gc

import adafruit_imageload
import board
import busio
import displayio
import terminalio
from adafruit_display_text import bitmap_label
from adafruit_gc9a01a import GC9A01A
from fourwire import FourWire

import config
from ui import colors
from ui import vga1_8x16


class Display:
    def __init__(self):
        displayio.release_displays()
        self.spi = busio.SPI(clock=config.DISPLAY_CLOCK, MOSI=config.DISPLAY_MOSI)
        self.bus = FourWire(
            self.spi,
            command=config.DISPLAY_DC,
            chip_select=config.DISPLAY_CS,
            reset=config.DISPLAY_RESET,
            baudrate=config.DISPLAY_BAUDRATE,
        )
        self.display = GC9A01A(
            self.bus,
            width=config.DISPLAY_WIDTH,
            height=config.DISPLAY_HEIGHT,
            rotation=0,
        )
        # The display module used on MaiBadge needs an explicit DISPON after
        # initialization.  This mirrors the known-working CircuitPython
        # prototype in code/circuitpython/code.py.
        self.bus.send(0x29, b"\x01")
        self.group = None
        self._resources = []
        self.show_solid(colors.BLACK)

    @staticmethod
    def rectangle(width, height, color, x=0, y=0):
        bitmap = displayio.Bitmap(width, height, 1)
        palette = displayio.Palette(1)
        palette[0] = color
        return displayio.TileGrid(bitmap, pixel_shader=palette, x=x, y=y)

    @staticmethod
    def label(text, x, y, color=colors.WHITE, scale=1):
        return bitmap_label.Label(
            terminalio.FONT,
            text=text,
            color=color,
            scale=scale,
            x=x,
            y=y,
        )

    def set_group(self, group, resources=None):
        old_group = self.group
        self.group = group
        self._resources = resources or []
        self.display.root_group = group
        del old_group
        gc.collect()

    def show_solid(self, color):
        group = displayio.Group()
        group.append(self.rectangle(config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, color))
        self.set_group(group)
        return group

    def image_group(self, filename):
        tile, resources = self.image_tile(filename)
        group = displayio.Group()
        group.append(tile)
        return group, resources

    @staticmethod
    def image_tile(filename, x=0, y=0):
        bitmap, palette = adafruit_imageload.load(filename)
        tile = displayio.TileGrid(bitmap, pixel_shader=palette, x=x, y=y)
        return tile, [bitmap, palette, tile]

    @staticmethod
    def pixel_text(text, x, y, color=colors.WHITE, background=colors.BLACK):
        """Render text with the original firmware's exact VGA 8x16 font."""
        width = max(1, len(text) * vga1_8x16.WIDTH)
        bitmap = displayio.Bitmap(width, vga1_8x16.HEIGHT, 2)
        palette = displayio.Palette(2)
        palette[0] = background
        palette[1] = color

        for char_index, character in enumerate(text):
            codepoint = ord(character)
            if codepoint < vga1_8x16.FIRST or codepoint > vga1_8x16.LAST:
                codepoint = ord("?")
            glyph_start = (codepoint - vga1_8x16.FIRST) * vga1_8x16.HEIGHT
            for row in range(vga1_8x16.HEIGHT):
                pixels = vga1_8x16.FONT[glyph_start + row]
                for column in range(vga1_8x16.WIDTH):
                    if pixels & (0x80 >> column):
                        bitmap[(char_index * vga1_8x16.WIDTH) + column, row] = 1

        tile = displayio.TileGrid(bitmap, pixel_shader=palette, x=x, y=y)
        return tile, [bitmap, palette, tile]

    def show_image(self, filename):
        group, resources = self.image_group(filename)
        self.set_group(group, resources)
        return group

    def show_error(self, message):
        group = displayio.Group()
        group.append(self.rectangle(240, 240, colors.DARK_PURPLE))
        group.append(self.label("MaiBadge error", 12, 28, colors.RED, 2))
        lines = self._wrap(str(message), 27)
        for index, line in enumerate(lines[:10]):
            group.append(self.label(line, 10, 64 + index * 15, colors.WHITE))
        group.append(self.label("Press reset after fixing files", 10, 224, colors.YELLOW))
        self.set_group(group)

    @staticmethod
    def _wrap(text, width):
        words = text.replace("\n", " ").split(" ")
        lines = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if len(candidate) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def deinit(self):
        displayio.release_displays()
