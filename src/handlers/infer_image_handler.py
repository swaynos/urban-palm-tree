import aiofiles
import asyncio
import logging

from game_state.game_state import GameState, get_game_states
from game_state.game_system_state import GameSystemState
from game_state.menu_state import MenuState, get_menu_states
from game_state.squad_battles_tracker import SquadBattlesTracker
from game_strategy.generic_game_strategy import GenericGameStrategy
from game_strategy.in_match_strategy import InMatchStrategy
from game_strategy.squad_battles_selection_menu_strategy import SquadBattlesSelectionMenuStrategy
from inference.yolo_object_detector import YoloObjectDetector
import utilities.config as config
import utilities.monitoring as monitoring
from controllers.game_flow_controller import GameFlowController
from utilities.image import ImageWrapper
from inference.image_classification_inference import ImageClassifier
from utilities.shared_thread_resources import exit_event

from inference.image_inference_pipeline import ImageInferencePipeline

infer_image_thread_statistics = monitoring.Statistics()

async def infer_image_handler(game: GameFlowController):
    """
    This method initiates a thread dedicated to performing image recognition tasks.
    It consumes images from ```shared_thread_resources.latest_screenshot``` and processes
    game state to ```shared_thread_resources.inferred_game_state```.
    """
    logger = logging.getLogger(__name__)

    # Import shared resources required for managing the lifecycle of the thread.
    # Moving the import to within the function ensures that the module is only imported when 
    # the function is called, which allows patching of these variables in tests.
    # `latest_screenshot` holds the most recent screenshot to be processed for inference
    # TODO: Is this still needed?
    from utilities.shared_thread_resources import latest_screenshot

    pipeline = ImageInferencePipeline(game, latest_screenshot, exit_event)
    await pipeline.start()
