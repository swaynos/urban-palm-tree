import asyncio
import json
import logging
from ollama_inference import infer_image_from_ollama
import monitoring
from sys import platform

from app_io import get_prompt
from game_controller import GameController
from shared_resources import exit_event, inferred_memory_collection
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
            # TODO: Only enter if the right window is active. (Annoying that keystrokes are entered while debugging)
            # memory = None
            # if (not inferred_memory_collection.empty()):
            #     memory = inferred_memory_collection.peek_n_latest(1)[0]
            
            # if memory is not None:
            #     response = memory[0]
            #     if (response["match-status"] == "IN-MATCH"
            #         and response["minimap"] == "YES"):
            #         logger.info("grabbing closest player and spinning in a circle for 3 seconds. Then tapping cross.")
            #         game.io.tap(game.io.L1)
            #         game.spin_in_circles(3)

            #     if (response["match-status"] == "IN-MENU"):
            #         await attempt_navigate_menu(game, memory[1])
            #         logger.info("tapping cross")
            #         game.io.tap(game.io.Cross)
                    
                #TODO: If the last 5 memories were IN-MENU, attempt to press cross to unblock the menu     
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)


# TODO: This was some test code for menu navigation. Rearchitect this next step.
async def attempt_navigate_menu(game: GameController, image: ImageWrapper):
    logger = logging.getLogger(__name__)
    # Squad Selection 2x2
    # cropped_image_base64 = image.return_region_as_base64(70,310,145,145)
    response = await infer_image_from_ollama(get_prompt("menu-is-squad-battles.txt"), image.scaled_as_base64(width=1280, height=720)) #cropped_image_base64)
    print (response)
    # try:
    #     responseJson = json.loads(response)
    # except json.JSONDecodeError:
    #     logger.error(response)
    #     responseJson = False
    # if responseJson:
    #     for move in responseJson:
    #         logger.info(f"tapping {move}")
    #         if move == "LEFT":
    #             game.io.tap(game.io.DPadLeft)
    #         elif move == "RIGHT":
    #             game.io.tap(game.io.DPadRight)
    #         elif move == "UP":
    #             game.io.tap(game.io.DPadUp)
    #         elif move == "DOWN":
    #             game.io.tap(game.io.DPadDown)
    #         elif move == "ENTER":
    #             game.io.tap(game.io.Cross)