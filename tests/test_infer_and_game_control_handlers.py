import asyncio
import logging
import os
import unittest

from PIL import Image as PILImage
from queue import Queue
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from controllers.game_flow_controller import GameFlowController
from handlers.game_control_handler import controller_input_handler
from controllers.game_strategy_controller import GameStrategyController
from game_state import GameState
from utilities.macos_app import RunningApplication
from utilities.shared_thread_resources import SharedProgramData
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
            os.path.join(screenshots_dir, path) for path in os.listdir(screenshots_dir) if path.endswith(('.png', '.jpg'))
        ]
        
        # Instantiate the shared program data
        self.shared_data = SharedProgramData()
        
        # Override the latest_screenshot queue methods to return images from image_queue
        self.shared_data.latest_screenshot.get = self.mock_get_image_from_queue
        self.shared_data.latest_screenshot.empty = lambda: self.image_queue.empty()

        # Populate the image queue with ImageWrapper objects created from the static screenshot paths
        for path in self.static_screenshot_paths:
            image = ImageWrapper(PILImage.open(path), path)
            self.image_queue.put(image)

        # Since we set the exit_event to stop the handler execution, 
        # clear the exit event to reset it before running each test
        self.shared_data.exit_event.clear()

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
        self.shared_data.exit_event.set()
        self.shared_data.inference_completed_event.set() # Wake up the controller handler if it's waiting
        return None
    
    # Test method to verify depletion of the test image queue
    @patch('inference.image_classification_inference.ImageClassifier.classify_image', return_value=GameState.IN_MATCH)
    async def test_image_queue_depletes(self, mock_classify_image):
        game = GameFlowController()

        await infer_image_handler(game, self.shared_data)

        # Assert that the image queue is empty after processing
        self.assertTrue(self.image_queue.empty())

    @patch('game_action.action.time.time')
    @patch('controllers.game_flow_controller.PlaystationIO', autospec=True)
    async def test_game_loop(self, mock_playstation_io, mock_time):
        # Mock time to increment to avoid busy wait loops in Action
        mock_time.side_effect = (i * 0.01 for i in range(1000000))

        app = Mock(spec=RunningApplication)
        game = GameFlowController()
        mock_playstation_io_instance = mock_playstation_io.return_value
        mock_playstation_io_instance.press_button = AsyncMock()
        mock_playstation_io_instance.hold_buttons = AsyncMock()
        # Configure buttons to avoid Action logging crash
        mock_playstation_io_instance.Cross = Mock()
        mock_playstation_io_instance.Cross.char = 'x'
        # Add others if needed by default random strategy?
        # get_action_from_button calls might use Lstick, R2, L1, Moon...
        # Let's mock a few common ones or ALL accessed attributes return something with char?
        # Simpler: Mock __getattr__? Too complex.
        # Just mock a few likely ones.
        mock_playstation_io_instance.Lstick.Left.char = 'Lstick.Left'
        mock_playstation_io_instance.Lstick.Right.char = 'Lstick.Right'
        mock_playstation_io_instance.Lstick.Up.char = 'Lstick.Up'
        mock_playstation_io_instance.R2.char = 'R2'
        mock_playstation_io_instance.L1.char = 'L1'
        mock_playstation_io_instance.Moon.char = 'Moon'


        mock_game_strategy = Mock(spec=GameStrategyController)
        mock_game_strategy.last_image = Mock()
        mock_game_strategy.last_image.get_timestamp.return_value = 0.0
        mock_game_strategy.image_inference_timestamp = 0.0
        mock_game_strategy.get_strategic_intent.return_value = None
        mock_game_strategy.is_in_match = AsyncMock(return_value=True) # or False depending on what we test? In loop test, it just builds actions.

        await asyncio.gather(
            infer_image_handler(game, self.shared_data),
            controller_input_handler(app, game, mock_game_strategy, self.shared_data),
            self.monitor_last_image_seen()
        )

        # This is a very expensive test that doesn't assert much, but it does ensure that the game loop runs without errors.
        
        # Assertions
        # tap is not called because action uses hold_buttons (since duration > 0)
        self.assertTrue(mock_playstation_io_instance.hold_buttons.called, "Expected hold_buttons method to be called for controller input.")
        # Additional assertions to check details about what was called on the mock.
    
    #TODO: before adding any new tests here, consider mocking the image classification
    # for the test, and writing the test in TestGameControlHandler instead of here.

if __name__ == '__main__':
    unittest.main()
