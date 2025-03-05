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
from utilities.shared_thread_resources import SharedProgramData

from inference.image_inference_pipeline import ImageInferencePipeline

infer_image_thread_statistics = monitoring.Statistics()

async def infer_image_handler(game: GameFlowController, shared_data: SharedProgramData):
    """
    This method initiates a thread dedicated to performing image recognition tasks.
    It consumes images from ```shared_thread_resources.latest_screenshot``` and processes
    game state to ```shared_thread_resources.inferred_game_state```.
    """
    logger = logging.getLogger(__name__)

    pipeline = ImageInferencePipeline(game, shared_data.latest_screenshot, exit_event)
    await pipeline.start()
