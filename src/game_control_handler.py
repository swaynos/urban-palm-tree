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
            current_game_state = await inferred_game_state.read_data()
            if current_game_state is not None:
                if current_game_state['GameState'] == GameState.IN_MATCH.name:
                    if ongoing_action is None:
                        logger.info("Game is in match, starting spin_in_circles.")
                        ongoing_action = create_ongoing_action(game.spin_in_circles(2))
                elif current_game_state['GameState'] == GameState.IN_MENU.name:
                    if ongoing_action is not None:
                        logger.info("Game is in menu, stopping spin_in_circles.")
                        try:
                            if not ongoing_action.done():
                                ongoing_action.cancel()  # This will stop the ongoing task
                                await ongoing_action
                        except asyncio.CancelledError:
                            logger.info("spin_in_circles was cancelled.")
                        ongoing_action = None
                    if current_game_state['MenuState'] == MenuState.SQUAD_BATTLES_OPPONENT_SELECTION.name:
                        logger.info(f"Game is at the {current_game_state['MenuState']}")
                        game.squad_battles_tracker.play_match()
                        await asyncio.sleep(1) # Sleep for 1s to allow the game to handle the input
                    elif current_game_state['MenuState'] is not None:
                        logger.info(f"Game is at the {current_game_state['MenuState']}. Tapping cross.")
                        game.io.tap(game.io.Cross)
                        await asyncio.sleep(.05) # Sleep for 50ms to allow the game to handle the input
                
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
