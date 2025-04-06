from pynput import keyboard as kb

import asyncio
import time

from typing import List

from utilities.playstation_io import PlaystationIO

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

    async def apply_steps(self):
        for step in self.steps:
            #TODO: Determine if the current action is stale
            # IDEA: look at the timestamp of the action and compare it to the latest image. If the image is newer
            # Argument: Even though there is a new image, there might not yet be a new action that needs to be executed
            # IDEA2: Keep it simple for now. Define in the configuration the maximum amount of time after an image is captured that an action can be executed
            if (step[1] > 0):
                await self.execute_action_over_time(step[0], step[1])
            else:
                await self.execute_action(step[0])

    async def execute_action(self, buttons: List[kb.KeyCode]):
        for button in buttons:
            await self.playstation_io.press_button(button)
        
    async def execute_action_over_time(self, buttons: List[kb.KeyCode], duration: float):
        end_time = time.time() + duration
        while time.time() < end_time: #TODO: I think we should remove this extra loop
            await self.playstation_io.hold_buttons(buttons, duration)

    async def steps_to_string(self):
        return_str = ""
        for step in self.steps:
            return_str += f"{step[0]} for {step[1]} seconds. "
        return return_str