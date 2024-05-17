import asyncio
import json
import logging
import monitoring
from typing import cast

from app_io import get_prompt
from game_controller import GameController
from inference import infer_image_from_ollama
from shared_resources import exit_event, inferred_memory_stack
from image import ImageWrapper
controller_input_thread_statistics = monitoring.Statistics()

# TODO: Check for active application before sending
async def controller_input_handler(game: GameController):
    """
    In this thread we will read input from a controller (a Playstation Controller, but could be any other type of controller) and perform actions based on that input.
    It uses the `controller` module to grab the latest input data for each button on the controller and performs actions based on those inputs.
    """
    logger = logging.getLogger(__name__)
    while(not exit_event.is_set()):
        try:
            # TODO: Only enter if the right window is active. (Annoying that keystrokes are entered while debugging)
            logger.debug(f"Has looped {controller_input_thread_statistics.count} times. Elapsed time is {controller_input_thread_statistics.get_time()}")
            
            memory = None
            if (not inferred_memory_stack.empty()):
                memory = inferred_memory_stack._queue[-1]
            
            if memory is not None:
                responseJson = memory[0]
                image = cast(ImageWrapper, memory[1])
                if (responseJson["match-status"] == "IN-MATCH"):
                    if (responseJson["live-match"] == "NO" or responseJson["instant-replay"] == "YES"):
                        logger.info("game is not in a live match, tapping cross")
                        game.io.tap(game.io.Cross)
                    else:
                        # press, release, tap to send input to the controller. Joystick movement is special.
                        logger.info("grabbing closest player and spinning in a circle")
                        game.io.tap(game.io.L1)
                        game.spin_in_circles(3)
                elif (responseJson["match-status"] == "IN-MENU"):
                    logger.info("attempting to navigate the menu")
                    await attempt_navigate_menu(game, image)
            
            controller_input_thread_statistics.count += 1
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
            # Just tap cross and see what happens
            game.io.tap(game.io.Cross)

async def attempt_navigate_menu(game: GameController, image: ImageWrapper):
    logger = logging.getLogger(__name__)
    # Squad Selection 2x2
    cropped_image_base64 = image.return_region_as_base64(70,310,145,145)
    response = await infer_image_from_ollama(get_prompt("menu-four-logos_prompt_returns-sequence.txt"), cropped_image_base64)
    try:
        responseJson = json.loads(response)
    except json.JSONDecodeError:
        logger.error(response)
        responseJson = False
    if responseJson:
        for move in responseJson:
            logger.info(f"tapping {move}")
            if move == "LEFT":
                game.io.tap(game.io.DPadLeft)
            elif move == "RIGHT":
                game.io.tap(game.io.DPadRight)
            elif move == "UP":
                game.io.tap(game.io.DPadUp)
            elif move == "DOWN":
                game.io.tap(game.io.DPadDown)
            elif move == "ENTER":
                game.io.tap(game.io.Cross)