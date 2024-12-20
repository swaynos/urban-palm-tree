from playstation_io import PlaystationIO
import asyncio
import time

from typing import List

# TODO: Redundancy in this implementation
class Action:
    def __init__(self, button_presses: List[str]):
        self.button_presses = button_presses
        self.io = PlaystationIO()

    async def execute_action(self, delay: float = 0.1):
        try:
            # Execute each button press in the list
            for button in self.button_presses:
                if hasattr(self.io, button):
                    # Press the button
                    self.io.tap(getattr(self.io, button))
                    await asyncio.sleep(delay)
        except asyncio.CancelledError:
            # Handle cancellation if needed
            self.io.release_all_buttons()  # Ensure all buttons are released
        finally:
            self.io.release_all_buttons()  # Ensure all buttons are released at the end

    # TODO: Test if this works as expected
    async def execute_action_over_time(self, duration: float, delay: float = 0.1):
        end_time = time.time() + duration
        try:
            while time.time() < end_time:
                # Execute each button press in the list
                for button in self.button_presses:
                    if hasattr(self.io, button):
                        # Press the button
                        self.io.tap(getattr(self.io, button))
                        await asyncio.sleep(delay)  # Adjust delay as needed
        except asyncio.CancelledError:
            # Handle cancellation if needed
            self.io.release_all_buttons()  # Ensure all buttons are released
        finally:
            self.io.release_all_buttons()  # Ensure all buttons are released at the end

    