"""Small lifecycle contract shared by all apps."""


class App:
    def __init__(self, hardware):
        self.hardware = hardware

    async def enter(self):
        pass

    def handle_event(self, event, now):
        return None

    def update(self, now):
        return None

    async def exit(self):
        self.hardware.safe_outputs()
