from game_controller import GameController
from pynput import keyboard as kb

import asyncio
import time

from typing import List

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
    def __init__(self, image_timestamp: float, infer_timestamp:float, game_controller: GameController, steps: List[tuple[List[kb.KeyCode], float]]):
        self.steps = steps
        self.game_controller = game_controller
        self.timestamps = [image_timestamp, infer_timestamp]

    async def apply_steps(self):
        for step in self.steps:
            if (step[1] > 0):
                await self.execute_action_over_time(step[0], step[1])
            else:
                await self.execute_action(step[0])

    async def execute_action(self, buttons: List[kb.KeyCode]):
        for button in buttons:
            await self.game_controller.press_button(button)
        
    async def execute_action_over_time(self, buttons: List[kb.KeyCode], duration: float):
        end_time = time.time() + duration
        while time.time() < end_time: #TODO: I think we should remove this extra loop
            await self.game_controller.hold_buttons(buttons, duration)

    async def steps_to_string(self):
        return_str = ""
        for step in self.steps:
            return_str += f"{step[0]} for {step[1]} seconds. "
        return return_str