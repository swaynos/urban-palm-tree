from game_state.game_state import GameState
from game_state.game_state_tracker import GameStateTracker
from utilities.shared_thread_resources import SharedObject


class GameStrategyController():
    def __init__(self):
        self.game_state_tracker = GameStateTracker()

    async def create_strategy(self):
        # TODO: inference activities should better populate the game state.
        # From the game state we can then build the strategy.
        raise NotImplementedError()
    
    async def is_in_match(self):
        return self.game_state_tracker.current_game_state == GameState.IN_MATCH