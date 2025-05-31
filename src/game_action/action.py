import logging
import time
from typing import List

from pynput import keyboard as kb

from utilities.playstation_io import PlaystationIO

logger = logging.getLogger(__name__)

class Action:
    """
    A class to handle actions within a game using the GameController.

    Attributes:
        steps (List[List[kb.KeyCode], float]): A list of steps where each step consists of a list of key codes and a float for timing.
        game_controller (GameController): An instance of GameController to manage game interactions.

    Methods:
        execute_action(buttons: List[kb.KeyCode]): 
            Presses the specified buttons one at a time using the game controller.

        execute_action_over_time(buttons: List[kb.KeyCode], duration: float): 
            Holds down all of the specified buttons for a given duration, periodically checking the elapsed time.
    """
    def __init__(self, image_timestamp: float, infer_timestamp:float, playstation_io: PlaystationIO, steps: List[tuple[List[kb.KeyCode], float]]):
        self.steps = steps
        self.playstation_io = playstation_io
        self.timestamps = [image_timestamp, infer_timestamp]

    def get_time_elapsed_from_screenshot(self):
        return time.time() - self.timestamps[0]
    
    def get_time_elapsed_from_inference(self):
        return time.time() - self.timestamps[1]

    async def apply_steps(self):
        for step in self.steps:
            if (step[1] > 0):
                await self.execute_action_over_time(step[0], step[1])
            else:
                await self.execute_action(step[0])

    async def execute_action(self, buttons: List[kb.KeyCode]):
        for button in buttons:
            logger.info(f"{await self.steps_to_string()}")
            logger.debug(f"Action: Time elapsed from screenshot: {self.get_time_elapsed_from_screenshot()}")
            logger.debug(f"Action: Time elapsed from inference: {self.get_time_elapsed_from_inference()}")
            await self.playstation_io.press_button(button)
        
    async def execute_action_over_time(self, buttons: List[kb.KeyCode], duration: float):
        end_time = time.time() + duration
        while time.time() < end_time:
            # TODO: There is a bug on macOS where these buttons get stuck within the running application.
            # Even after termination of this runtime, the buttons remain stuck.
            logger.info(f"{await self.steps_to_string()}")
            logger.debug(f"Action: Time elapsed from screenshot: {self.get_time_elapsed_from_screenshot()}")
            logger.debug(f"Action: Time elapsed from inference: {self.get_time_elapsed_from_inference()}")
            await self.playstation_io.hold_buttons(buttons, duration)

    async def steps_to_string(self):
        return_str = ""
        for step in self.steps:
            keys = ', '.join([key.char if hasattr(key, 'char') else str(key) for key in step[0]])
            return_str += f"Pressing keys: {keys} for {step[1]} seconds. "
        return return_str