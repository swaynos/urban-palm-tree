import json
import logging
import requests
import threading
import time
from sys import platform

# urban-palm-tree imports
if platform == "darwin":
    from macos_app_io import activate_app, find_app, get_image_from_window, get_prompt
elif platform == "linux" or platform == "linux2":
    from linux_app_io import Foo

from image import ImageWrapper
from game_controller import GameController
from window import get_window
import config as config
import monitoring as monitoring

# Begin Program
app = find_app(config.APP_NAME)
pid = app.processIdentifier()
game = GameController()

# TODO: Remove or place in another file
def compare_image_to_screenshot(image, screenshot_name):
    ssimResult = image.compare_ssim(screenshot_name)
    logging.info("SSIM Result for screeshot is {} for screenshot {}".format(ssimResult, screenshot_name))

# Begin Threading
# Create a mutex object for the most recent screenshot
latest_screenshots_mutex = threading.Lock()
latest_screenshots_stack = []

# Create a statistics object for each thread
capture_image_thread_statistics = monitoring.Statistics()
infer_image_thread_statistics = monitoring.Statistics()
controller_input_thread_statistics = monitoring.Statistics()


def capture_image_thread():
    """
    In this thread we will capture a screenshot of the desired application and stores it in a global variable for later use.
    It uses the `get_window` and `ImageWrapper` functions from the `app_io` module to grab the window and create an image object.
    The image is then locked with the `latest_screenshot_mutex` lock, ensuring that only one thread can access it at a time.
    """
    while(app):
        try:
            logging.debug(f"capture_image_thread: Has looped {capture_image_thread_statistics.count} times. Elapsed time is {capture_image_thread_statistics.get_time()}")
            if not activate_app(app):
                logging.error("capture_image_thread: app activation failed")
            logging.info("capture_image_thread: Grabbing a screenshot")
            window = get_window(pid)
            image = ImageWrapper(get_image_from_window(window))
            # Lock the image so that if another thread is trying to read, we aren't overwritting it
            with latest_screenshots_mutex:
                # clear the stack if it gets too big
                if (len(latest_screenshots_stack) > 10):
                    latest_screenshots_stack.clear()
                latest_screenshots_stack.append(image)
            capture_image_thread_statistics.count += 1
        except Exception as argument:
            logging.error(argument)

def infer_image_thread():
    """
    In this thread we will perform an image recognition task on the most recent screenshot captured by the `capture_image_thread`.
    It uses the `ImageWrapper` and `get_prompt` functions from the `app_io` module to grab a prompt and create an image object.
    The inferred image is then stored in a global variable for later use, ensuring that only one thread can access it at a time.
    """
    while(True):
        try:
            image = None
            with latest_screenshots_mutex:
                if (len(latest_screenshots_stack) > 0):
                    image = latest_screenshots_stack.pop()
            if(image != None):
                logging.debug("infer_image_thread: Has looped {} times. Elapsed time is {}".format(infer_image_thread_statistics.count, infer_image_thread_statistics.get_time()))
                logging.info("infer_image_thread: inferring image from latest screenshot using ollama")
                payload = {
                    "model": "llava",
                    "prompt": get_prompt("screenshot_prompt.txt"),
                    "stream": False,
                    "images": [f"{image.scaled_as_base64()}"]
                }
                response = requests.post(config.OLLAMA_URL, json=payload)
                responseObj = json.loads(response.text)
                logging.info(responseObj['response']) # TODO: do something
            else:
                logging.debug("infer_image_thread: There is not a latest screenshot to infer from")
                time.sleep(1)
            infer_image_thread_statistics.count += 1
        except Exception as argument:
            logging.error(argument)
    
def controller_input_thread():
    """
    In this thread we will read input from a controller (a Playstation Controller, but could be any other type of controller) and perform actions based on that input.
    It uses the `controller` module to grab the latest input data for each button on the controller and performs actions based on those inputs.
    """
    while(True):
        try:
            # TODO: Only enter if the right window is active. (Annoying that keystrokes are entered while debugging)
            logging.debug(f"controller_input_thread: Has looped {controller_input_thread_statistics.count} times. Elapsed time is {controller_input_thread_statistics.get_time()}")

            # press, release, tap to send input to the controller. Joystick movement is special.
            logging.info("controller_input_thread: going to corner")

            game.go_to_corner(1)
            
            controller_input_thread_statistics.count += 1
        except Exception as argument:
            logging.error(argument)

# Create a new Thread object for each function
capture_image_thread_instance = threading.Thread(target=capture_image_thread)
infer_image_thread_instance = threading.Thread(target=infer_image_thread)
controller_input_thread_instance = threading.Thread(target=controller_input_thread)
# TODO: another thread to read user input???

# Start the threads
activate_app(app)
capture_image_thread_instance.start()
infer_image_thread_instance.start()
controller_input_thread_instance.start()

capture_image_thread_instance.join()
infer_image_thread_instance.join()
controller_input_thread_instance.join()