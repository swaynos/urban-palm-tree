import logging

import utilities.monitoring as monitoring
from controllers.game_strategy_controller import GameStrategyController
from utilities.shared_thread_resources import SharedProgramData
from inference.image_inference_pipeline import ImageInferencePipeline

infer_image_thread_statistics = monitoring.Statistics()

async def infer_image_handler(game: GameStrategyController, shared_data: SharedProgramData):
    """
    This method initiates a thread dedicated to performing image recognition tasks.
    It consumes images from ```shared_thread_resources.latest_screenshot``` and processes
    game state to the GameStrategyController.
    """
    logger = logging.getLogger(__name__)

    pipeline = ImageInferencePipeline(game, shared_data.latest_screenshot, shared_data.exit_event)
    await pipeline.start()
