import logging
import random
import time
from controllers.game_strategy_controller import GameStrategyController
from game_action.action import Action
from utilities.playstation_io import PlaystationIO

from game_state.menu_state import MenuState
from game_state.squad_battles_tracker import SquadBattlesTracker

class GameFlowController():
    def __init__(self):
        self.io = PlaystationIO()
        self.logger = logging.getLogger(__name__)
        self.squad_battles_tracker = SquadBattlesTracker()

    async def build_actions_from_strategy(self, game_strategy: GameStrategyController):
        """
        Builds a list of actions to be performed based on the current game state and strategy.
        """
        actions = []
        
        # Check for explicit strategic intent from Fast Path
        intent = game_strategy.get_strategic_intent()
        
        if intent:
            # We have a specific plan from the Vision/Strategy layer
            image_timestamp = game_strategy.last_image.get_timestamp() if game_strategy.last_image else time.time()
            infer_timestamp = game_strategy.image_inference_timestamp if game_strategy.image_inference_timestamp else time.time()
            
            if intent == "FAST_MOVE_LEFT":
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Lstick.Left, 0.1))
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.R2, 0.1)) # Sprint
            elif intent == "FAST_MOVE_RIGHT":
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Lstick.Right, 0.1))
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.R2, 0.1)) # Sprint
            elif intent == "FAST_SPRINT_FORWARD":
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Lstick.Up, 0.1))
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.R2, 0.1)) # Sprint
                
            self.logger.info(f"Generated actions for intent: {intent}")
            return actions

        # Helper to safely get timestamps
        def get_timestamps():
             t1 = game_strategy.last_image.get_timestamp() if game_strategy.last_image else time.time()
             t2 = game_strategy.image_inference_timestamp if game_strategy.image_inference_timestamp else time.time()
             return t1, t2

        # Check Menu State for Squad Battles
        menu_state = game_strategy.get_menu_state()
        if menu_state == MenuState.SQUAD_BATTLES_OPPONENT_SELECTION:
            image_timestamp, infer_timestamp = get_timestamps()
            
            # Capture current position
            current_row = self.squad_battles_tracker.current_row
            current_col = self.squad_battles_tracker.current_col
            
            # Update tracker (virtual play)
            self.squad_battles_tracker.play_match()
            
            # Capture new position
            next_row = self.squad_battles_tracker.current_row
            next_col = self.squad_battles_tracker.current_col
            
            # Action 1: Select (Play logic uses Cross)
            actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.Cross, 0.1))
            
            # Action 2: Navigate physically to match virtual state
            if next_col > current_col:
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.DPadRight, 0.1))
            elif next_col < current_col:
                # Wrap around or move left? Tests don't specify, but generally Right -> Down -> Left -> Left?
                # SquadBattlesTracker 2x2:
                # 0,0 -> 0,1 (Right)
                # 0,1 -> 1,1 (Down)
                # 1,1 -> 1,0 (Left)
                # 1,0 -> 0,0 (Up)
                actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.DPadLeft, 0.1))
                
            if next_row > current_row:
                 actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.DPadDown, 0.1))
            elif next_row < current_row:
                 actions.append(self.get_action_from_button(image_timestamp, infer_timestamp, self.io.DPadUp, 0.1))

            return actions

        is_in_match = await game_strategy.is_in_match()
        if is_in_match:
            # Fallback legacy random behavior if no intent is present
            image_timestamp, infer_timestamp = get_timestamps()
            
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
            image_timestamp, infer_timestamp = get_timestamps()
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