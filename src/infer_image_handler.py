import json
import logging
import requests
import time

import config
import monitoring
from shared_resources import exit_event, screenshots_stack, inferred_memory_stack
from app_io import get_prompt

infer_image_thread_statistics = monitoring.Statistics()

def infer_image_handler():
    """
    In this thread we will perform an image recognition task on the most recent screenshot captured by the `capture_image_thread`.
    It uses the `ImageWrapper` and `get_prompt` functions from the `app_io` module to grab a prompt and create an image object.
    The inferred image is then stored in a global variable for later use, ensuring that only one thread can access it at a time.
    """
    while(not exit_event.is_set()):
        try:
            image = None
            memory = None
            if (not screenshots_stack.empty()):
                image = screenshots_stack.get_nowait()
            if (not inferred_memory_stack.empty()):
                memory = inferred_memory_stack._queue[-1]
            if(image != None):
                # TODO: throwaway code
                screenshotFilename = "screenshots/new-screenshot{}.png"
                image._image.save(screenshotFilename.format(time.time()))

                logging.debug("infer_image_thread: Has looped {} times. Elapsed time is {}".format(infer_image_thread_statistics.count, infer_image_thread_statistics.get_time()))
                logging.info("infer_image_thread: inferring image from latest screenshot using ollama")
                prompt = get_prompt("screenshot_prompt.txt")
                if(memory is not None):
                    prompt = prompt + f"In the last screenshot, your response was {memory}"
                payload = {
                    "model": "_llava",
                    "prompt": prompt,
                    "stream": False,
                    "images": [f"{image.scaled_as_base64()}"]
                }
                response = requests.post(config.OLLAMA_URL, json=payload)
                responseObj = json.loads(response.text)
                inferred_memory_stack.put_nowait(responseObj['response'].strip(" "))
                logging.info(responseObj['response']) # TODO: figure out logging
                print(responseObj['response']) # TODO: Do something more useful here
            else:
                logging.debug("infer_image_thread: There is not a latest screenshot to infer from")
                time.sleep(1)
            infer_image_thread_statistics.count += 1
        except Exception as argument:
            logging.error(argument)