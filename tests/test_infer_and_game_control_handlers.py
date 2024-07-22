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

        # Retrieve paths of static screenshots in the directory
        self.static_screenshot_paths = [
            os.path.join(screenshots_dir, path) for path in os.listdir(screenshots_dir) if path.endswith('.png')
        ]
        
        # Populate the image queue with ImageWrapper objects created from the static screenshot paths
        for path in self.static_screenshot_paths:
            image = ImageWrapper(PILImage.open(path))
            self.image_queue.put(image)

        # Since we set the exit_event to stop the handler execution, 
        # clear the exit event to reset it before running each test
        exit_event.clear()

    async def mock_get_image_from_queue(self):
        if not self.image_queue.empty():
            return self.image_queue.get()
        else:
            # If the queue is empty, set the exit event to stop the handler execution
            exit_event.set()
        return None
    
    # Test method to verify depletion of the test image queue
    @patch('shared_resources.latest_screenshot', new_callable=Mock)
    @patch('image_classification_inference.ImageClassifier.classify_image', return_value=GameState.IN_MATCH)
    async def test_image_queue_depletes(self, mock_classify_image, mock_latest_screenshot):
        # Mock methods for latest_screenshot
        mock_latest_screenshot.empty.return_value = False
        mock_latest_screenshot.get.side_effect = self.mock_get_image_from_queue
        await infer_image_handler()

        # Assert that the image queue is empty after processing
        self.assertTrue(self.image_queue.empty())

    @patch('shared_resources.latest_screenshot', new_callable=Mock)
    @patch('game_controller.PlaystationIO', new_callable=Mock)
    async def test_game_loop(self, mock_playstation_io, mock_latest_screenshot):
        # Mock methods for latest_screenshot
        mock_latest_screenshot.empty.return_value = False
        mock_latest_screenshot.get.side_effect = self.mock_get_image_from_queue

        app = Mock(spec=RunningApplication)
        game = GameController()
        mock_playstation_io_instance = mock_playstation_io.return_value

        await asyncio.gather(
            infer_image_handler(),
            controller_input_handler(app, game)
        )

        # This is a very expensive test that doesn't assert much, but it does ensure that the game loop runs without errors.

        # Assertions
        self.assertTrue(mock_playstation_io_instance.tap.called, "Expected tap method to be called for controller input.")
        self.assertTrue(inferred_game_state.data is not None, "Expected inferred_game_state to have been updated.")
        # Additional assertions to check details about what was called on the mock.

if __name__ == '__main__':
    unittest.main()
