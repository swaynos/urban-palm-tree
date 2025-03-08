import asyncio
import logging
from utilities import config
import utilities.monitoring as monitoring

from controllers.game_strategy_controller import GameStrategyController
from utilities.macos_app import RunningApplication
from utilities.shared_thread_resources import SharedProgramData

controller_input_thread_statistics = monitoring.Statistics()

# TODO: Consider controller_input_handler as a class with better dependency injection
def create_ongoing_action(coro):
    """
    Create an ongoing action as a task.
    This function can be patched in tests.
    """
    return asyncio.create_task(coro)

# TODO: Check for active application before sending
async def controller_input_handler(app: RunningApplication, game: GameStrategyController, shared_data: SharedProgramData):
    """
    In this thread we will read input from a controller (a Playstation Controller, but could be any other type of controller) and perform actions based on that input.
    It uses the `controller` module to grab the latest input data for each button on the controller and performs actions based on those inputs.
    """
    logger = logging.getLogger(__name__)

    while(not shared_data.exit_event.is_set()):
        logger.debug(f"controller_input_handler has looped {controller_input_thread_statistics.count} times. Elapsed time is {controller_input_thread_statistics.get_time()}")
        controller_input_thread_statistics.count += 1
        try:
            current_game_state = await shared_data.inferred_game_state.read_data()
            if current_game_state is not None:
                # TODO: Do work
                await asyncio.sleep(.05) # Sleep for 50ms to allow the game to handle the input
                
            await asyncio.sleep(config.CONTROLLER_INPUT_THREAD_DELAY)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
