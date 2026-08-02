"""Eight chained addressable RGB LEDs."""

import neopixel

import config


class Leds:
    COLORS = (
        (0, 0, 0),
        (32, 16, 0),
        (0, 32, 32),
        (32, 0, 0),
        (32, 0, 32),
        (0, 0, 32),
    )

    def __init__(self):
        self._pixels = neopixel.NeoPixel(
            config.PIXEL_PIN,
            config.PIXEL_COUNT,
            brightness=config.PIXEL_BRIGHTNESS,
            auto_write=False,
        )
        self.color_index = 0
        self.off()

    def set_all(self, color):
        self._pixels.fill(color)
        self._pixels.show()

    def set_pixel(self, index, color):
        """Set one physical lane LED without changing the remaining lanes."""
        self._pixels[index % config.PIXEL_COUNT] = color
        self._pixels.show()

    def next_color(self):
        self.color_index = (self.color_index + 1) % len(self.COLORS)
        self.set_all(self.COLORS[self.color_index])
        return self.COLORS[self.color_index]

    def off(self):
        self.set_all((0, 0, 0))

    def deinit(self):
        self._pixels.deinit()
