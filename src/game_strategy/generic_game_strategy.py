import time
from game_action.action import Action
from game_controller import GameController
from game_state.game_system_state import GameSystemState

class GenericGameStrategy:
    def __init__(self, game_system_state: GameSystemState):
        self.menu_state = game_system_state

    def determine_action_from_state(self, image_timestamp:float, game_controller: GameController) -> list[Action]: 
        steps = []

        # TODO: Implement logging of decisions based on state
        steps.append([[game_controller.io.Cross],0])

        infer_timestamp = time.time()

        return Action(image_timestamp, infer_timestamp ,game_controller, steps)