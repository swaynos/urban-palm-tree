import asyncio
import json
import logging

from inference import infer_image_from_ollama, parse_json_response
import monitoring
from shared_resources import exit_event, latest_screenshot, inferred_memory_collection
from app_io import get_prompt

infer_image_thread_statistics = monitoring.Statistics()

async def infer_image_handler():
    """
    In this thread we will perform an image recognition task on the most recent screenshot captured by the `capture_image_thread`.
    It uses the `ImageWrapper` and `get_prompt` functions from the `app_io` module to grab a prompt and create an image object.
    The inferred image is then stored in a global variable for later use, ensuring that only one thread can access it at a time.
    """
    logger = logging.getLogger(__name__)
    while(not exit_event.is_set()):
        try:
            # Update statistics for monitoring purposes
            logger.debug("Has looped {} times. Elapsed time is {}".format(infer_image_thread_statistics.count, infer_image_thread_statistics.get_time()))
            infer_image_thread_statistics.count += 1

            image = None
            if (not latest_screenshot.empty()):
                image = await latest_screenshot.get()

            # Re-introduce this code if you want to use the last memory to enhance the prompt.
            # memory = None
            # if (not inferred_memory_collection.empty()):
            #     memory = inferred_memory_collection.peek_n_latest(1)

            if(image != None):
                logger.debug("inferring image from latest screenshot using ollama")
                prompt = get_prompt("match-status_prompt_returns-json.txt")
   
                response_str = await infer_image_from_ollama(prompt, image.scaled_as_base64())
                response = await parse_json_response(logger, response_str)

                if (response!= None):
                    await inferred_memory_collection.append([response, image])
                    logger.info("Inferred match-status is {}".format(response.get("match-status")))
            else:
                logger.warning("There is not a latest screenshot to infer from")
            
            await asyncio.sleep(0)  # Yield control back to the event loop
        except json.JSONDecodeError as jsonDecodeError:
            logger.error(f"Error parsing the json response: {response}")
            logger.error(jsonDecodeError)
        except Exception as argument:
            logger.error(argument)