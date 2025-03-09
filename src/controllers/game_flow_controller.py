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
        # TODO: Implement the logic to build actions based on the game state and strategy
        return actions
    
    async def execute_actions(self, actions: list[Action]):
        pass