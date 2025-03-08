import asyncio
import time

from pynput import keyboard as kb
from typing import List

from controllers.game_strategy_controller import GameStrategyController
from utilities.playstation_io import PlaystationIO

class GameFlowController():
    def __init__(self):
        self.io = PlaystationIO()
        self.actions = []

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

    # TODO: Come up with a better way to combine multiple streams of input
    # For example, while pressing the left joystick to upper left, I also want to tap
    # A every 50 ms, and then B every 200ms. How might that input be combined in a way 
    # where the syntax doesn't get too messy?
    async def do_something_long(self, duration):
        end_time = time.time() + duration
        try:
            while time.time() < end_time:
                # Just garbage input to show a couple of techniques using pynput
                with kb.Controller.pressed(kb.Key.shift, kb.KeyCode(char='\\')):
                    kb.Controller.tap(kb.Key.enter)
                    await asyncio.sleep(0.25)  # Keep it pressed for 0.25 seconds

        except asyncio.CancelledError:
            # Add any cleanup code if needed here when cancelled
            # Notify about cancellation if needed
            pass
        finally:
            self.io.release_all_buttons() # Ensure all buttons are released
            pass

    async def build_actions(self, game_strategy: GameStrategyController):
        """
        Builds a list of actions to be performed based on the current game state and strategy.
        """
        # TODO: Implement the logic to build actions based on the game state and strategy
        # self.actions
        pass