import random
import time
from controllers.game_strategy_controller import GameStrategyController
from game_action.action import Action
from utilities.playstation_io import PlaystationIO

class GameFlowController():
    def __init__(self):
        self.io = PlaystationIO()

    async def build_actions_from_strategy(self, game_strategy: GameStrategyController):
        """
        Builds a list of actions to be performed based on the current game state and strategy.
        """
        actions = []
        
        # TODO: Determine if I want to continue to use these timestamps, and provide actual values
        image_timestamp = time.time()
        infer_timestamp = time.time()

        is_in_match = await game_strategy.is_in_match()
        if is_in_match:
            random_bool = True #random.choice([True, False])
            # Select nearest and pass
            if random_bool:
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.L1, 0))
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 0.05))
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 1))
            else:
                pass
        else:
            actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 0))
        
        return actions
    
    async def execute_actions(self, actions: list[Action]):
        for action in actions:
            await action.apply_steps()
    
    def get_action_from_button(self, infer_timestamp: float, image_timestamp: float, button, duration: float = 0):
        press_button_steps = [([button], duration)]
        return Action(image_timestamp, infer_timestamp, self.io, press_button_steps)