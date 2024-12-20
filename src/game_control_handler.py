import asyncio
import json
import logging
from ollama_inference import infer_image_from_ollama
import monitoring
from sys import platform

from app_io import get_prompt
from game_controller import GameController
from game_state import GameState, MenuState
if platform == "darwin":
    from macos_app import RunningApplication
elif platform == "linux" or platform == "linux2":
    from linux_app import RunningApplication
from image import ImageWrapper
from shared_resources import exit_event

controller_input_thread_statistics = monitoring.Statistics()

# TODO: Consider controller_input_handler as a class with better dependency injection
def create_ongoing_action(coro):
    """
    Create an ongoing action as a task.
    This function can be patched in tests.
    """
    return asyncio.create_task(coro)

# TODO: Check for active application before sending
async def controller_input_handler(app: RunningApplication, game: GameController):
    """
    In this thread we will read input from a controller (a Playstation Controller, but could be any other type of controller) and perform actions based on that input.
    It uses the `controller` module to grab the latest input data for each button on the controller and performs actions based on those inputs.
    """
    logger = logging.getLogger(__name__)

    # Import shared resources required for managing the lifecycle of the thread.
    # Moving the import to within the function ensures that the module is only imported when 
    # the function is called, which allows patching of these variables in tests.
    from shared_resources import latest_actions_sequence

    ongoing_action = None

    while(not exit_event.is_set()):
        logger.debug(f"Has looped {controller_input_thread_statistics.count} times. Elapsed time is {controller_input_thread_statistics.get_time()}")
        controller_input_thread_statistics.count += 1
        try:
            raise NotImplementedError("Method needs to be rewritten")
            #TODO: Complete the implementation.
            # 1. Validate that an action sequence isn't in progress (`ongoing_action`)
            # 2. Set `ongoing_action`
            # 3. Read the latest actions from the latest_actions_sequence
            # 4. Perform actions
            # 5. Clear `ongoing_action`
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
