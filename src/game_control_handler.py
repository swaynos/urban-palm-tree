import asyncio
import json
import logging
from ollama_inference import infer_image_from_ollama
import monitoring
from sys import platform

from app_io import get_prompt
from game_controller import GameController
from game_state import GameState, MenuState
from shared_resources import exit_event, inferred_memory_collection, inferred_game_state
if platform == "darwin":
    from macos_app import RunningApplication
elif platform == "linux" or platform == "linux2":
    from linux_app import RunningApplication
from image import ImageWrapper
controller_input_thread_statistics = monitoring.Statistics()

# TODO: Check for active application before sending
async def controller_input_handler(app: RunningApplication, game: GameController):
    """
    In this thread we will read input from a controller (a Playstation Controller, but could be any other type of controller) and perform actions based on that input.
    It uses the `controller` module to grab the latest input data for each button on the controller and performs actions based on those inputs.
    """
    logger = logging.getLogger(__name__)
    while(not exit_event.is_set()):
        logger.debug(f"Has looped {controller_input_thread_statistics.count} times. Elapsed time is {controller_input_thread_statistics.get_time()}")
        controller_input_thread_statistics.count += 1
        try:
            current_game_state = await inferred_game_state.read_data()

            if current_game_state is not None and current_game_state['GameState'] == GameState.IN_MATCH.name:
                logging.info("Game is in match, not sending controller input")
                # TODO: Do something in-match
            elif current_game_state is not None and current_game_state['GameState'] == GameState.IN_MENU.name:
                if (current_game_state['MenuState'] == MenuState.SQUAD_BATTLES_OPPONENT_SELECTION.name):
                    logging.info(f"Game is at the {current_game_state['MenuState']}")
                    # TODO: Do something in the opponent selection menu
                    #
                    #
                elif (current_game_state['MenuState'] != MenuState.UNKNOWN.name):
                    logging.info(f"Game is at the {current_game_state['MenuState']}. Tapping cross.")
                    game.io.tap(game.io.Cross)
                
            await asyncio.sleep(5)  # TODO: Remove
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
