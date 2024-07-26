import aiofiles
import asyncio
import logging

import config
import monitoring
from game_state.game_state import GameState, get_game_states
from game_state.menu_state import MenuState, get_menu_states
from image import ImageWrapper
from image_classification_inference import ImageClassifier
from app_io import get_prompt
from shared_resources import exit_event

infer_image_thread_statistics = monitoring.Statistics()

async def infer_image_handler():
    """
    In this thread we will perform an image recognition task on the most recent screenshot captured by the `capture_image_thread`.
    It uses the `ImageWrapper` and `get_prompt` functions from the `app_io` module to grab a prompt and create an image object.
    The inferred image is then stored in a global variable for later use, ensuring that only one thread can access it at a time.
    """
    logger = logging.getLogger(__name__)

    # Import shared resources required for managing the lifecycle of the thread.
    # Moving the import to within the function ensures that the module is only imported when 
    # the function is called, which allows patching of these variables in tests.
    # `latest_screenshot` holds the most recent screenshot to be processed for inference
    from shared_resources import latest_screenshot, inferred_game_state, inferred_memory_collection
    
    # Initialize the menu vs. match image classifier
    menu_vs_match_classes = get_game_states()
    menu_states_classes = get_menu_states()
    game_status_image_classifier = ImageClassifier(config.HF_MENU_VS_MATCH_PATH, config.MENU_VS_MATCH_FILENAME, menu_vs_match_classes)
    menu_status_image_classifier = ImageClassifier(config.HF_MENU_CLASSIFICATION_PATH, config.IN_MENU_CLASSIFICATION_FILENAME, menu_states_classes)
    while(not exit_event.is_set()):
        try:
            # Update statistics for monitoring purposes
            logger.debug(f"Has looped {infer_image_thread_statistics.count} times. Elapsed time is {infer_image_thread_statistics.get_time()}")
            infer_image_thread_statistics.count += 1

            image: ImageWrapper = None
            if (not latest_screenshot.empty()):
                image = await latest_screenshot.get()

            if(image is not None):
                game_status_response, game_status_predictions = await game_status_image_classifier.classify_image(image)
                
                # Append the current inferred state as a tuple
                inferred_state = {
                    'GameState': game_status_response.name,
                    'MenuState': None,
                    'MatchState': None,
                }
                logger.info(f"The currently inferred state of the game is {game_status_response.name}")

                inferred_memory_collection.append(inferred_state)

                # Check if all the latest inferred states are the same
                latest_states = inferred_memory_collection.peek_n_latest(5)
                all_states_equal = True
                last_state = None
                for state in latest_states:
                    if last_state is not None:
                        all_states_equal = all_states_equal and state['GameState'] == last_state['GameState']
                        # TODO: MenuState and MatchState?
                    last_state = state
                if all_states_equal:
                    logger.info(f"The last 5 inferred states are all the same: {last_state['GameState']}.")
                    if inferred_state['GameState'] == GameState.IN_MENU.name:
                        menu_status_response, menu_status_predictions = await menu_status_image_classifier.classify_image(image)
                        
                        inferred_state['MenuState'] = menu_status_response.name
                        logger.info(f"The currently inferred menu state of the game is {menu_status_response.name}")
                    logger.info(f"Updating the shared inferred_game_state.")
                    await inferred_game_state.update_data(inferred_state)
            else:
                logger.warning("There is not a latest screenshot to infer from")
            
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)
