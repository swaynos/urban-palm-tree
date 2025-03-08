import asyncio
import logging
import time

from controllers.game_strategy_controller import GameStrategyController
from inference.game_state_inference import GameStateInference
from inference.menu_state_inference import MenuStateInference
from inference.rush_inference import RushInference
from inference.squad_selection_inference import SquadSelectionInference
from utilities.image import ImageWrapper

class ImageInferencePipeline:
    def __init__(self, game: GameStrategyController, latest_screenshot_queue: asyncio.Queue, stop_event: asyncio.Event):
        self.game = game
        self.latest_screenshot_queue = latest_screenshot_queue
        self.stop_event = stop_event
        self.logger = logging.getLogger(__name__)

    async def start(self):
        """Starts the inference pipeline."""

        while not self.stop_event.is_set():
            try:
                if not self.latest_screenshot_queue.empty():
                    image = await self.latest_screenshot_queue.get()
                    if image:
                        await self.process_image(image)
                        self.logger.debug(f"Time elapsed for image inference: {image.compare_timestamp(time.time())}")
                    else:
                        self.logger.warning("No image available for inference.")
                        await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Inference pipeline error: {e}")
            
            await asyncio.sleep(0)  # Yield control back to the event loop

    async def process_image(self, image: ImageWrapper):
        """Processes an image through the inference pipeline."""
        first_inference = RushInference()
        first_inference.set_next(GameStateInference()).set_next(MenuStateInference()).set_next(SquadSelectionInference())

        await first_inference.execute(image, self.game)
        