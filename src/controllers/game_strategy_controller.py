import time

from game_state.game_state import GameState
from game_state.game_state_tracker import GameStateTracker
from typing import Optional
from utilities.image import ImageWrapper

# TODO: Use logic from game_strategy objects to determine actions
class GameStrategyController():
    def __init__(self):
        self.game_state_tracker = GameStateTracker()

        # The last image used for inference
        self.last_image: Optional[ImageWrapper] = None
        # The timestamp of when the last inference completed
        self.image_inference_timestamp = None

    async def create_strategy(self):
        # TODO: inference activities should better populate the game state.
        # From the game state we can then build the strategy.
        raise NotImplementedError()
    
    async def update_inference_timestamp(self):
        self.image_inference_timestamp = time.time()
        return self.image_inference_timestamp

    async def set_last_image(self, image):
        self.last_image = image

    async def is_in_match(self):
        return self.game_state_tracker.current_game_state == GameState.IN_MATCH