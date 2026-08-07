"""Eight chained addressable RGB LEDs."""

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
    COLORS = (
        (0, 0, 0),
        (32, 16, 0),
        (0, 32, 32),
        (32, 0, 0),
        (32, 0, 32),
        (0, 0, 32),
    )
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
        self.color_index = 0
        self.mode_index = 0
        self.frame = 0
        self.next_frame_at = 0.0
        self.off()

    @property
    def mode_name(self):
        return self.MODES[self.mode_index][0]

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

    def next_mode(self, now):
        self.mode_index = (self.mode_index + 1) % len(self.MODES)
        self.frame = 0
        self.next_frame_at = now
        self._render_mode()
        return self.mode_name

    def update(self, now):
        if self.mode_name in (
            "off",
            "red",
            "green",
            "blue",
            "cyan",
            "magenta",
            "amber",
            "white",
        ):
            return
        if now < self.next_frame_at:
            return
        self._render_mode()
        self.frame = (self.frame + 1) & 255
        self.next_frame_at = now + config.ANIMATION_INTERVAL

    def _render_mode(self):
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
            for offset, level in enumerate((255, 96, 32)):
                self._pixels[(head - offset) % config.PIXEL_COUNT] = (level, 0, level)
        elif name == "pulse":
            phase = self.frame % 32
            level = phase * 16 if phase < 16 else (31 - phase) * 16
            self._pixels.fill((0, level, level))
        self._pixels.show()

    def off(self):
        self.set_all((0, 0, 0))

    def deinit(self):
        self._pixels.deinit()
