import asyncio
import time
from typing import List

from playstation_io import PlaystationIO
from pynput import keyboard as kb

class GameController():
    def __init__(self):
        self.io = PlaystationIO()

    async def press_button(self, button: kb.KeyCode, duration: float = 0.1):
        try:
            # Press the button
            self.io.tap(button)
            await asyncio.sleep(duration)
        except asyncio.CancelledError:
            # Handle cancellation if needed
            self.io.release(button)
        finally:
            self.io.release(button)  # Ensure the button is released at the end

    async def hold_buttons(self, buttons: List[kb.KeyCode], duration: float = 0.5):
        try:
            with self.io.pressed(*buttons):
                await asyncio.sleep(duration)
        except asyncio.CancelledError:
            # Handle cancellation if needed
            for button in buttons:
                self.io.release(button)
        finally:
            # Ensure the buttons are released at the end
            for button in buttons:
                self.io.release(button)  