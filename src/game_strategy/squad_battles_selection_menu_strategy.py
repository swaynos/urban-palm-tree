import time
from game_action.action import Action
from controllers.game_flow_controller import GameFlowController
from game_state.squad_battles_tracker import SquadBattlesTracker

class SquadBattlesSelectionMenuStrategy:
    """
    A strategy class that determines actions based on the state of the squad battles tracker.

    Attributes:
        tracker (SquadBattlesTracker): An instance of SquadBattlesTracker that keeps track of the match states.
    """

    def __init__(self, tracker: SquadBattlesTracker):
        """
        Initializes the SquadBattlesSelectionMenuStrategy object with a SquadBattlesTracker instance.

        Parameters:
            tracker (SquadBattlesTracker): An instance of the tracker to be used for determining actions.
        """
        self.tracker = tracker
        
    @staticmethod
    def describe_strategy():
        description_str = "Squad Battles Selection Menu Strategy"
        return description_str
    
    # TODO: Write Unit Tests
    def determine_action_from_state(self, image_timestamp: float, game_controller: GameFlowController) -> list[Action]:
        """
        Determines a list of actions to execute based on the current state of the grid in the tracker.

        Returns:
            list[Action]: A list of Action objects representing the determined actions.
        """
        steps = []

        # If the top row is selected
        if self.tracker.current_row < 0:
            steps.append([[game_controller.io.DPadDown],0])

        selected_squad_valid = True

        # Check the state of each match in the 2x2 grid
        for row in range(2):
            for col in range(2):
                 # If match played at the current selection
                if self.tracker.current_row == row \
                    and self.tracker.current_col == col \
                        and self.tracker.grid[row][col]:
                    # Determine the action based on the match position
                    if row == 0 and col == 0:
                        selected_squad_valid = False
                        steps.append([[game_controller.io.DPadRight],0])
                        break
                    elif row == 0 and col == 1:
                        selected_squad_valid = False
                        steps.append([[game_controller.io.DPadDown],0])
                        break
                    elif row == 1 and col == 1:
                        selected_squad_valid = False
                        steps.append([[game_controller.io.DPadLeft],0])
                        break
                    elif row == 1 and col == 0:
                        selected_squad_valid = False
                        steps.append([[game_controller.io.DPadUp],0])
                        break
        
        if (selected_squad_valid):
            steps.append([[game_controller.io.Cross],150])

        infer_timestamp = time.time()

        return Action(image_timestamp, infer_timestamp, game_controller, steps)