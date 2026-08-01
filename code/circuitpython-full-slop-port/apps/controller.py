"""Single-owner application state machine."""

import asyncio
import gc
import time

import config
from apps.diagnostics import DiagnosticsApp
from apps.face import FaceApp
from apps.game import GameApp
from apps.menu import MenuApp
from apps.song_app import SongApp
from ui import colors


class Controller:
    def __init__(self, hardware):
        self.hardware = hardware
        self.app = None

    def _make_app(self, action):
        if action == "face":
            return FaceApp(self.hardware)
        if action == "menu":
            return MenuApp(self.hardware)
        if action.startswith("song_"):
            return SongApp(self.hardware, action)
        if action == "game":
            return GameApp(self.hardware)
        if action == "diagnostics":
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
        display = self.hardware.display
        group = display.show_solid(colors.DARK_PURPLE)
        group.append(display.label("MaiBadge", 44, 96, colors.PINK, 3))
        group.append(display.label("Calibrating touch...", 38, 145, colors.WHITE))
        await self.hardware.calibrate()
        print("Touch calibration:")
        for entry in self.hardware.touch.snapshot():
            print(entry)

        await self._switch("face")
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
