"""Solid colours and non-blocking animations for eight NeoPixels."""

import neopixel

import config


def color_wheel(position):
    """Return an RGB rainbow colour for a position from 0 through 255."""
    position = position & 255
    if position < 85:
        return (255 - position * 3, position * 3, 0)
    if position < 170:
        position -= 85
        return (0, 255 - position * 3, position * 3)
    position -= 170
    return (position * 3, 0, 255 - position * 3)


class Leds:
    MODES = (
        ("off", None),
        ("red", (255, 0, 0)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("cyan", (0, 255, 255)),
        ("magenta", (255, 0, 255)),
        ("amber", (255, 96, 0)),
        ("white", (255, 255, 255)),
        ("rainbow", None),
        ("chase", None),
        ("comet", None),
        ("pulse", None),
    )

    def __init__(self):
        self._pixels = neopixel.NeoPixel(
            config.PIXEL_PIN,
            config.PIXEL_COUNT,
            brightness=config.PIXEL_BRIGHTNESS,
            auto_write=False,
        )
        self.mode_index = 0
        self.frame = 0
        self.next_frame_at = 0.0
        self.off()

    @property
    def mode_name(self):
        return self.MODES[self.mode_index][0]

    def next_mode(self, now):
        self.mode_index = (self.mode_index + 1) % len(self.MODES)
        self.frame = 0
        self.next_frame_at = now
        self._render()
        return self.mode_name

    def update(self, now):
        mode = self.mode_name
        if mode in ("off", "red", "green", "blue", "cyan", "magenta", "amber", "white"):
            return
        if now < self.next_frame_at:
            return
        self._render()
        self.frame = (self.frame + 1) & 255
        self.next_frame_at = now + config.ANIMATION_INTERVAL

    def _render(self):
        name, color = self.MODES[self.mode_index]
        if name == "off":
            self._pixels.fill((0, 0, 0))
        elif color is not None:
            self._pixels.fill(color)
        elif name == "rainbow":
            for index in range(config.PIXEL_COUNT):
                offset = (index * 256) // config.PIXEL_COUNT
                self._pixels[index] = color_wheel(offset + self.frame * 5)
        elif name == "chase":
            self._pixels.fill((0, 0, 0))
            self._pixels[self.frame % config.PIXEL_COUNT] = (0, 255, 255)
        elif name == "comet":
            self._pixels.fill((0, 0, 0))
            head = self.frame % config.PIXEL_COUNT
            levels = (255, 96, 32)
            for offset, level in enumerate(levels):
                self._pixels[(head - offset) % config.PIXEL_COUNT] = (level, 0, level)
        elif name == "pulse":
            phase = self.frame % 32
            level = phase * 16 if phase < 16 else (31 - phase) * 16
            self._pixels.fill((0, level, level))
        self._pixels.show()

    def off(self):
        self._pixels.fill((0, 0, 0))
        self._pixels.show()

    def deinit(self):
        self._pixels.deinit()
