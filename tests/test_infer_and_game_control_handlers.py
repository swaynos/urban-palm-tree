import asyncio
import os
import unittest

from PIL import Image as PILImage
from queue import Queue
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from game_controller import GameController
from game_control_handler import controller_input_handler
from game_state.game_state import GameState
from image import ImageWrapper
from infer_image_handler import infer_image_handler
from macos_app import RunningApplication
from shared_resources import exit_event, latest_screenshot, inferred_game_state, inferred_memory_collection

# Static values for testing
screenshots_dir = "static_screenshots"
target_resolution=(480, 270) # Models should have been trained at this resolution

class TestInferAndGameControlHandlers(unittest.IsolatedAsyncioTestCase):
    # Set up the initial state before running each test method
    def setUp(self):
        # Initialize the Queue to hold images
        self.image_queue = Queue()
        latest_screenshot = self.image_queue

        # Retrieve paths of static screenshots in the directory
        self.static_screenshot_paths = [
            os.path.join(screenshots_dir, path) for path in os.listdir(screenshots_dir) if path.endswith('.png')
        ]
        
        # Populate the image queue with ImageWrapper objects created from the static screenshot paths
        for path in self.static_screenshot_paths:
            image = PILImage.open(path)
            self.image_queue.put(image)

        # Since we set the exit_event to stop the handler execution, 
        # clear the exit event to reset it before running each test
        exit_event.clear()

    async def mock_get_image_from_queue(self):
        if not self.image_queue:
            return None
        return self.image_queue.get()
    
    # Test method to verify depletion of the test image queue
    @patch('shared_resources.latest_screenshot', side_effect=Mock)
    @patch('image_classification_inference.ImageClassifier.classify_image', return_value=GameState.IN_MATCH)
    async def test_image_queue_depletes(self, mock_classify_image, mock_latest_screenshot):
        # Define mock for grabbing the latest screenshot
        # Define empty() conditions
        def custom_get_screenshot_empty_side_effect():
            return False
        mock_latest_screenshot.empty.return_value = custom_get_screenshot_empty_side_effect  
        # Define exit conditions (when no more sreenshots are left)
        async def custom_get_screenshot_side_effect():
            screenshot = await self.mock_get_image_from_queue()
            if screenshot is None:
                exit_event.set()
                # Create empty image 480x270 to prevent errors
                #screenshot = PILImage.new('RGBA', target_resolution)
            return screenshot
        mock_latest_screenshot.get.side_effect = custom_get_screenshot_side_effect

        await infer_image_handler()

        # Assert that the image queue is empty after processing
        self.assertTrue(self.image_queue.empty())
    
    @patch('game_controller.PlaystationIO')
    async def test_game_loop(self, mock_get_screenshot, mock_playstation_io):
        # Define mock for grabbing the latest screenshot
        # Define exit conditions (when no more sreenshots are left)
        async def custom_get_screenshot_side_effect():
            screenshot = await self.mock_get_image_from_queue()
            if screenshot is None:
                exit_event.set()
            return screenshot
        mock_get_screenshot.side_effect = custom_get_screenshot_side_effect

        app = Mock(spec=RunningApplication)
        mock_io = Mock()  # Create a new Mock object
        mock_playstation_io.return_value = mock_io  # Patch the io attribute with the Mock object

        # Instantiate the GameController
        game = GameController()

        await asyncio.gather(
            infer_image_handler(),
            controller_input_handler(app, game)
        )

        # Assertions
        # TODO: What to assert for?

if __name__ == '__main__':
    unittest.main()
