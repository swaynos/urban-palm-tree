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

    # New methods for Fast Path
    async def update_strategy(self, detections: list, image_width: int):
        """
        Updates the current strategic intent based on object detections.
        """
        self.strategic_intent = None # Reset
        
        # Simple Ball Chasing Logic
        ball = next((d for d in detections if d['class_name'] == 'ball'), None)
        
        if ball:
            ball_x = ball['points']['x']
            ball_center = ball_x + (ball['points']['width'] / 2)
            screen_center = image_width / 2
            
            # Tolerance to avoid jitter
            tolerance = image_width * 0.1 
            
            if ball_center < (screen_center - tolerance):
                self.strategic_intent = "FAST_MOVE_LEFT"
            elif ball_center > (screen_center + tolerance):
                self.strategic_intent = "FAST_MOVE_RIGHT"
            else:
                self.strategic_intent = "FAST_SPRINT_FORWARD" # Ball is roughly in front
        else:
            # No ball seen? default to nothing or hold position
             self.strategic_intent = None

    def get_strategic_intent(self):
        return getattr(self, 'strategic_intent', None)

    def get_menu_state(self):
        return self.game_state_tracker.current_menu_state