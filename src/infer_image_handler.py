import aiofiles
import asyncio
import logging

import config
from game_state.game_state import GameState, get_game_states
from image import ImageWrapper
from image_classification_inference import ImageClassifier
import monitoring
from shared_resources import exit_event, latest_screenshot, inferred_game_state, inferred_memory_collection
from app_io import get_prompt

infer_image_thread_statistics = monitoring.Statistics()

async def infer_image_handler():
    """
    In this thread we will perform an image recognition task on the most recent screenshot captured by the `capture_image_thread`.
    It uses the `ImageWrapper` and `get_prompt` functions from the `app_io` module to grab a prompt and create an image object.
    The inferred image is then stored in a global variable for later use, ensuring that only one thread can access it at a time.
    """
    logger = logging.getLogger(__name__)

    # Initialize the menu vs. match image classifier
    menu_vs_match_classes = get_game_states()
    menu_vs_match_modelpath = "menu_vs_match_model.h5"
    image_classifier = ImageClassifier(menu_vs_match_modelpath, menu_vs_match_classes)

    while(not exit_event.is_set()):
        try:
            # Update statistics for monitoring purposes
            logger.debug(f"Has looped {infer_image_thread_statistics.count} times. Elapsed time is {infer_image_thread_statistics.get_time()}")
            infer_image_thread_statistics.count += 1

            image: ImageWrapper = None
            if (not latest_screenshot.empty()):
                image = await latest_screenshot.get()

            if(image is not None):
                #logger.debug("inferring image from latest screenshot using ollama")
                #prompt = get_prompt("match-status_prompt_returns-json.txt")
   
                # response_str = await infer_image_from_ollama(prompt, image.scaled_as_base64(width=1280, height=720))
                # response = await parse_json_response(logger, response_str)

                # if (response is not None):
                #     inferred_memory_collection.append([response, image])
                #     logger.info("Inferred match-status is {}".format(response["match-status"]))
                
                # if (config.SAVE_SCREENSHOT_RESPONSE and image.saved_path is not None):
                #     save_path = image.saved_path.replace(".png", "-response.json")
                #     async with aiofiles.open(save_path, 'w') as out_file:
                #         await out_file.write(response_str)
                logger.debug(f"inferring image from latest screenshot using {menu_vs_match_modelpath}")
                response = await image_classifier.classify_image(image)

                # Append the current inferred state as a tuple
                inferred_state = {
                    'GameState': response.name,
                    'MenuState': None,
                    'MatchState': None,
                }
                inferred_memory_collection.append(inferred_state)

                # Check if all the latest inferred states are the same
                latest_states = inferred_memory_collection.peek_n_latest(10)
                all_states_equal = True
                last_state = None
                for state in latest_states:
                    if last_state is not None:
                        all_states_equal = all_states_equal and state['GameState'] == last_state['GameState']
                        # TODO: MenuState and MatchState?
                    last_state = state
                if all_states_equal:
                    await inferred_game_state.update_data(inferred_state)
                # TODO: Consider a more robust strategy that uses the internal score from classify_image() to determine if the state has changed, or at least provide weight to the most recent states.

                logger.info(f"Inferred match-status is {response.name}")
                logger.info(f"The inferred_state of the game is: {await inferred_game_state.read_data()}")
            else:
                logger.warning("There is not a latest screenshot to infer from")
            
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
