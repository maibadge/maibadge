"""Calibrated capacitive-touch input for the eight MaiBadge electrodes."""

import asyncio
import touchio

import config


class TouchChannel:
    def __init__(self, name, pin):
        self.name = name
        self.input = touchio.TouchIn(pin)
        self.baseline = self.input.raw_value
        self.pressed = False
        self._candidate = False
        self._candidate_count = 0
        self._set_thresholds()

    def _set_thresholds(self):
        self.press_threshold = self.baseline + config.TOUCH_PRESS_MARGIN
        self.release_threshold = self.baseline + config.TOUCH_RELEASE_MARGIN
        # We compare raw_value ourselves to provide hysteresis.  Do not write
        # TouchIn.threshold here: ESP32-S3 can briefly report 65535 on the
        # first sample, which would make baseline + margin invalid (> 65535).

    def set_baseline(self, value):
        self.baseline = int(value)
        self._set_thresholds()

    def sample(self):
        raw = self.input.raw_value
        target = raw > (self.release_threshold if self.pressed else self.press_threshold)

        if target == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate = target
            self._candidate_count = 1

        changed = None
        if target != self.pressed and self._candidate_count >= config.TOUCH_STABLE_SAMPLES:
            self.pressed = target
            changed = target

        # Slowly follow environmental drift only while confidently untouched.
        if not self.pressed and raw < self.press_threshold:
            self.baseline = ((self.baseline * 127) + raw) // 128
            self._set_thresholds()

        return raw, changed

    def deinit(self):
        self.input.deinit()


class TouchPads:
    def __init__(self):
        self.channels = [TouchChannel(name, pin) for name, pin in config.TOUCH_CONFIG]
        self._raw = {channel.name: channel.input.raw_value for channel in self.channels}

    async def calibrate(self, samples=None):
        count = samples or config.TOUCH_CALIBRATION_SAMPLES
        totals = [0] * len(self.channels)
        for _ in range(count):
            for index, channel in enumerate(self.channels):
                totals[index] += channel.input.raw_value
            await asyncio.sleep(0.01)

        for index, channel in enumerate(self.channels):
            channel.set_baseline(totals[index] // count)
            self._raw[channel.name] = channel.input.raw_value

    def poll(self):
        result = []
        for channel in self.channels:
            raw, changed = channel.sample()
            self._raw[channel.name] = raw
            if changed is not None:
                result.append(("press" if changed else "release", "touch", channel.name))
        return result

    def snapshot(self):
        return tuple(
            (
                channel.name,
                self._raw[channel.name],
                channel.baseline,
                channel.press_threshold,
                channel.pressed,
            )
            for channel in self.channels
        )

    def deinit(self):
        for channel in self.channels:
            channel.deinit()
