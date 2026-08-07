"""Single-owner application state machine."""

import asyncio
import gc
import time

import config
from ui import colors


class Controller:
    def __init__(self, hardware):
        self.hardware = hardware
        self.app = None

    def _make_app(self, action):
        if action == "headless":
            from apps.headless import HeadlessApp

            return HeadlessApp(self.hardware)
        if action == "color":
            from apps.color import ColorApp

            return ColorApp(self.hardware)
        if action == "face":
            from apps.face import FaceApp

            return FaceApp(self.hardware)
        if action == "menu":
            from apps.menu import MenuApp

            return MenuApp(self.hardware)
        if action.startswith("song_"):
            from apps.song_app import SongApp

            return SongApp(self.hardware, action)
        if action == "game":
            if not config.ENABLE_GAME:
                raise ValueError("Game is disabled for " + config.VARIANT)
            from apps.game import GameApp

            return GameApp(self.hardware)
        if action == "diagnostics":
            from apps.diagnostics import DiagnosticsApp

            return DiagnosticsApp(self.hardware)
        raise ValueError("Unknown app action: " + action)

    async def _switch(self, action):
        if self.app is not None:
            await self.app.exit()
        self.hardware.safe_outputs()
        self.app = self._make_app(action)
        gc.collect()
        await self.app.enter()

    async def run(self):
        if not config.HAS_DISPLAY:
            await self._switch("headless")
            await self._run_loop()
            return

        display = self.hardware.display
        splash_started = time.monotonic()
        try:
            group, resources = display.image_group(config.SPLASH_IMAGE)
            status_color = colors.DARK_PURPLE
        except (OSError, ValueError):
            group = display.show_solid(colors.DARK_PURPLE)
            group.append(display.label("MaiBadge", 44, 96, colors.PINK, 3))
            resources = []
            status_color = colors.WHITE

        status_x = max(0, 120 - ((len(config.STARTUP_STATUS) * 8) // 2))
        calibrating, owned = display.pixel_text(
            config.STARTUP_STATUS,
            status_x,
            184,
            status_color,
            transparent=True,
        )
        ready, ready_owned = display.pixel_text(
            "READY!",
            96,
            184,
            status_color,
            transparent=True,
        )
        ready.hidden = True
        group.append(calibrating)
        group.append(ready)
        resources.extend(owned)
        resources.extend(ready_owned)
        display.set_group(group, resources)

        await self.hardware.calibrate()
        if config.HAS_TOUCH:
            print("Touch calibration:")
            for entry in self.hardware.touch.snapshot():
                print(entry)

        remaining = config.SPLASH_MIN_SECONDS - (time.monotonic() - splash_started)
        if remaining > 0:
            await asyncio.sleep(remaining)
        calibrating.hidden = True
        ready.hidden = False
        await asyncio.sleep(config.SPLASH_READY_SECONDS)

        await self._switch(config.START_APP)
        await self._run_loop()

    async def _run_loop(self):
        while True:
            now = time.monotonic()
            action = None
            for event in self.hardware.poll_events():
                requested = self.app.handle_event(event, now)
                if requested is not None:
                    action = requested
                    break
            if action is None:
                action = self.app.update(now)
            if action is not None:
                await self._switch(action)
            await asyncio.sleep(config.CONTROLLER_INTERVAL)
