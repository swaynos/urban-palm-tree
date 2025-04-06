import logging
import random
import time
from controllers.game_strategy_controller import GameStrategyController
from game_action.action import Action
from utilities.playstation_io import PlaystationIO

class GameFlowController():
    def __init__(self):
        self.io = PlaystationIO()
        self.logger = logging.getLogger(__name__)

    async def build_actions_from_strategy(self, game_strategy: GameStrategyController):
        """
        Builds a list of actions to be performed based on the current game state and strategy.
        """
        # TODO: can game_strategy_controller return the actions directly? Using objects from game_strategy?
        actions = []
        
        # TODO: Determine if I want to continue to use these timestamps, and provide actual values
        image_timestamp = time.time()
        infer_timestamp = time.time()

        is_in_match = await game_strategy.is_in_match()
        if is_in_match:
            # Loop it 10 times to avoid waiting for long inference
            for i in range(10):
                random_number = random.randint(1, 10)
                # Select nearest and pass
                if random_number > 1:
                    actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.L1, 0))
                    actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 0.05))
                    actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 1))
                # Shoot it
                else:
                    actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Moon, 0.05))
            # Spin in circles, then pass
            # else:
            #     [game_controller.io.L2, game_controller.io.Lstick.Left],0.5])
            #     [[game_controller.io.L2, game_controller.io.Lstick.Up],0.5])
            #     [[game_controller.io.L2, game_controller.io.Lstick.Right],0.5])
            #     [[game_controller.io.L2, game_controller.io.Lstick.Down],0.5])
            #     [[game_controller.io.Cross],0])
        else:
            actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 0))
        
        return actions
    
    async def execute_actions(self, actions: list[Action]):
        for action in actions:
            earliest_time = min(action.timestamps)
            elapsed_time = time.time() - earliest_time
            self.logger.debug(f"Executing action | elapsed time from image capture to action execution: {elapsed_time}")
            await action.apply_steps()
    
    def get_action_from_button(self, infer_timestamp: float, image_timestamp: float, button, duration: float = 0):
        press_button_steps = [([button], duration)]
        return Action(image_timestamp, infer_timestamp, self.io, press_button_steps)