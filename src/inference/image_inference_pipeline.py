import asyncio
import logging

from controllers.game_flow_controller import GameFlowController
from inference.game_state_inference import GameStateInference
from inference.menu_state_inference import MenuStateInference
from inference.squad_selection_inference import SquadSelectionInference
from utilities.image import ImageWrapper

class ImageInferencePipeline:
    def __init__(self, game: GameFlowController, latest_screenshot_queue: asyncio.Queue, stop_event: asyncio.Event):
        self.game = game
        self.logger = logging.getLogger(__name__)
        self.task_queue = asyncio.Queue()
        self.latest_screenshot_queue = latest_screenshot_queue
        self.stop_event = stop_event

    async def start(self):
        """Starts the inference pipeline."""

        while not self.stop_event.is_set():
            try:
                if not self.latest_screenshot_queue.empty():
                    image = await self.latest_screenshot_queue.get()
                    if image:
                        await self.process_image(image)
                    else:
                        self.logger.warning("No image available for inference.")
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Inference pipeline error: {e}")
            
            await asyncio.sleep(0)  # Yield control back to the event loop

    async def process_image(self, image: ImageWrapper):
        """Processes an image through the inference pipeline."""
        first_inference = GameStateInference()
        first_inference.set_next(MenuStateInference()).set_next(SquadSelectionInference())

        result = await first_inference.execute(image, self.game)
        await self.task_queue.put(result)
        