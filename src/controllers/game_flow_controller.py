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
        
        is_in_match = await game_strategy.is_in_match()
        if is_in_match:
            # These should not be empty if we are in a match
            image_timestamp = game_strategy.last_image.get_timestamp()
            infer_timestamp = game_strategy.image_inference_timestamp
            
            # TODO: This is a placeholder for the actual strategy, to simulate different behaviors that can outcome
            random_number = random.randint(1, 10)
            
            # Select nearest (L1) and hold X for 300ms
            if random_number > 1:
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.L1, 0))
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 0.3))
            # Shoot it
            else:
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Moon, 0.05))
            
            # Idea: Spin in circles, then pass
            # else:
            #     [game_controller.io.L2, game_controller.io.Lstick.Left],0.5])
            #     [[game_controller.io.L2, game_controller.io.Lstick.Up],0.5])
            #     [[game_controller.io.L2, game_controller.io.Lstick.Right],0.5])
            #     [[game_controller.io.L2, game_controller.io.Lstick.Down],0.5])
            #     [[game_controller.io.Cross],0])
        elif game_strategy.last_image is not None \
            and game_strategy.image_inference_timestamp is not None:
            image_timestamp = game_strategy.last_image.get_timestamp()
            infer_timestamp = game_strategy.image_inference_timestamp
            actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 0))
        
        return actions
    
    async def execute_actions(self, actions: list[Action]):
        for action in actions:
            earliest_time = min(action.timestamps)
            elapsed_time = time.time() - earliest_time
            self.logger.debug(f"Executing action | elapsed time from image capture to action execution: {elapsed_time}")
            await action.apply_steps()
    
    def get_action_from_button(self, image_timestamp: float, infer_timestamp: float, button, duration: float = 0):
        press_button_steps = [([button], duration)]
        return Action(image_timestamp, infer_timestamp, self.io, press_button_steps)