import asyncio
import logging
import os
import unittest

from PIL import Image as PILImage
from queue import Queue
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from controllers.game_flow_controller import GameFlowController
from handlers.game_control_handler import controller_input_handler
from game_state import GameState
from utilities.macos_app import RunningApplication
from utilities.shared_thread_resources import exit_event, latest_screenshot, inferred_game_state, inferred_memory_collection
from utilities.image import ImageWrapper
from handlers.infer_image_handler import infer_image_handler

# Static values for testing
screenshots_dir = "static_screenshots"
target_resolution=(480, 270) # Models should have been trained at this resolution

class TestInferAndGameControlHandlers(unittest.IsolatedAsyncioTestCase):
    # Set up the initial state before running each test method
    def setUp(self):
        # Configure the logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize the Queue to hold images
        self.image_queue = Queue()

        # Keep track of the last image seen by the handler
        self.last_image_seen = None

        # Retrieve paths of static screenshots in the directory
        self.static_screenshot_paths = [
            os.path.join(screenshots_dir, path) for path in os.listdir(screenshots_dir) if path.endswith('.png')
        ]
        
        # Populate the image queue with ImageWrapper objects created from the static screenshot paths
        for path in self.static_screenshot_paths:
            image = ImageWrapper(PILImage.open(path), path)
            self.image_queue.put(image)

        # Since we set the exit_event to stop the handler execution, 
        # clear the exit event to reset it before running each test
        exit_event.clear()

    async def monitor_last_image_seen(self):
        """
        Monitors the last image seen by checking the image queue and performing additional actions based on the value of self.last_image_seen.

        This method runs in a loop until the image queue is empty or until the `is_running` flag is set to False.

        Returns:
            None
        """
        is_running = True
        while is_running:
            if self.image_queue.empty():
                is_running = False
            if self.last_image_seen is not None:
                self.logger.debug(f"Last image seen: {self.last_image_seen.saved_path}")
                # Perform any additional actions based on the value of self.last_image_seen

            # Sleep for a very short amount of time to avoid blocking the event loop
            # 12 ms is about the inference time for a single image on good hardware
            await asyncio.sleep(.012)

    async def mock_get_image_from_queue(self):
        """
        Retrieves an image from the image queue.

        If the image queue is not empty, the method retrieves the next image from the queue and updates the `last_image_seen` attribute.
        If the image queue is empty, the method sets the exit event to stop the handler execution.

        Returns:
            The retrieved image from the queue, or None if the queue is empty.
        """
        if not self.image_queue.empty():
            self.last_image_seen = self.image_queue.get()
            return self.last_image_seen
        
        # If the queue is empty, set the exit event to stop the handler execution
        exit_event.set()
        return None
    
    # Test method to verify depletion of the test image queue
    @patch('shared_thread_resources.latest_screenshot', new_callable=Mock)
    @patch('image_classification_inference.ImageClassifier.classify_image', return_value=GameState.IN_MATCH)
    async def test_image_queue_depletes(self, mock_classify_image, mock_latest_screenshot):
        # Mock methods for latest_screenshot
        mock_latest_screenshot.empty.return_value = False
        mock_latest_screenshot.get.side_effect = self.mock_get_image_from_queue
        await infer_image_handler()

        # Assert that the image queue is empty after processing
        self.assertTrue(self.image_queue.empty())

    @patch('shared_thread_resources.latest_screenshot', new_callable=Mock)
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
            controller_input_handler(app, game),
            self.monitor_last_image_seen()
        )

        # This is a very expensive test that doesn't assert much, but it does ensure that the game loop runs without errors.

        # Assertions
        self.assertTrue(mock_playstation_io_instance.tap.called, "Expected tap method to be called for controller input.")
        self.assertTrue(inferred_game_state.data is not None, "Expected inferred_game_state to have been updated.")
        # Additional assertions to check details about what was called on the mock.
    
    #TODO: before adding any new tests here, consider mocking the image classification
    # for the test, and writing the test in TestGameControlHandler instead of here.

if __name__ == '__main__':
    unittest.main()
