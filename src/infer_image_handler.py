import asyncio
import json
import logging

from inference import infer_image_from_ollama
import monitoring
from shared_resources import exit_event, screenshots_stack, inferred_memory_stack
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
            image = None
            memory = None
            if (not screenshots_stack.empty()):
                image = await screenshots_stack.get()
            if (not inferred_memory_stack.empty()):
                memory = inferred_memory_stack._queue[-1]
            if(image != None):
                logger.debug("Has looped {} times. Elapsed time is {}".format(infer_image_thread_statistics.count, infer_image_thread_statistics.get_time()))
                logger.debug("inferring image from latest screenshot using ollama")
                prompt = get_prompt("match-status_prompt_returns-json.txt")
                if(memory is not None):
                    prompt = prompt + f" In the last screenshot, your response was {memory}."
                response = await infer_image_from_ollama(prompt, image.scaled_as_base64())
                responseObjJson = json.loads(response) # Prompt expects templated json response
                # TODO: What happens when the response isn't json?
                await inferred_memory_stack.put([responseObjJson, image])
                logger.info("Inferred match-status is {}".format(responseObjJson["match-status"]))
            else:
                logger.warning("There is not a latest screenshot to infer from")
            infer_image_thread_statistics.count += 1
            await asyncio.sleep(0)  # Yield control back to the event loop
        except json.JSONDecodeError as jsonDecodeError:
            logger.error(f"Error parsing the json response: {response}")
            logger.error(jsonDecodeError)
        except Exception as argument:
            logger.error(argument)