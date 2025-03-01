import asyncio
import json
import logging
import utilities.monitoring as monitoring

from controllers.game_flow_controller import GameFlowController
from utilities.macos_app import RunningApplication
from utilities.image import ImageWrapper
from utilities.shared_thread_resources import exit_event

controller_input_thread_statistics = monitoring.Statistics()

# TODO: Consider controller_input_handler as a class with better dependency injection
def create_ongoing_action(coro):
    """
    Create an ongoing action as a task.
    This function can be patched in tests.
    """
    return asyncio.create_task(coro)

# TODO: Check for active application before sending
async def controller_input_handler(app: RunningApplication, game: GameFlowController):
    """
    In this thread we will read input from a controller (a Playstation Controller, but could be any other type of controller) and perform actions based on that input.
    It uses the `controller` module to grab the latest input data for each button on the controller and performs actions based on those inputs.
    """
    logger = logging.getLogger(__name__)

    # Import shared resources required for managing the lifecycle of the thread.
    # Moving the import to within the function ensures that the module is only imported when 
    # the function is called, which allows patching of these variables in tests.
    # `inferred_game_state` holds the most recent inferred game state
    from utilities.shared_thread_resources import inferred_memory_collection, inferred_game_state

    ongoing_action = None # This will be used to store an io task that is currently running

    while(not exit_event.is_set()):
        logger.debug(f"Has looped {controller_input_thread_statistics.count} times. Elapsed time is {controller_input_thread_statistics.get_time()}")
        controller_input_thread_statistics.count += 1
        try:
            current_game_state = await inferred_game_state.read_data()
            if current_game_state is not None:
                # TODO: Do work
                await asyncio.sleep(.05) # Sleep for 50ms to allow the game to handle the input
                
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
