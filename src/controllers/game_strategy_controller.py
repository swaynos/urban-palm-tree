from utilities.shared_thread_resources import SharedObject


class GameStrategyController():
    def __init__(self):
        self.game_state = SharedObject()

    async def create_strategy(self):
        # TODO: inference activities should better populate the game state.
        # From the game state we can then build the strategy.
        raise NotImplementedError()