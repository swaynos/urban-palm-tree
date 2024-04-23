from AppKit import NSApplicationActivateAllWindows, NSApplicationActivateIgnoringOtherApps
import json
import pynput
import requests

# urban-palm-tree imports
from app_io import find_app, get_image_from_window, get_prompt
from image import ImageWrapper
from window import get_window
import config as config
import monitoring as monitoring

# Begin Program
app = find_app(config.APP_NAME)
pid = app.processIdentifier()
statistics = monitoring.Statistics()

def compare_image_to_screenshot(image, screenshot_name):
    ssimResult = image.compare_ssim(screenshot_name)
    print("SSIM Result for screeshot is {} for screenshot {}".format(ssimResult, screenshot_name))

# Loop
while(app):
    print("Has looped {} times. Elapsed time is {}".format(statistics.count, statistics.get_time()))
    # app.isActive: Indicates whether the application is currently frontmost.
    if not (app.isActive()):
        print("{} is not active, attempting to active. Activation Policy = {}.".format(config.APP_NAME, app.activationPolicy()))
        """
        Activation Policy: https://developer.apple.com/documentation/appkit/nsapplicationactivationpolicy?language=objc
        ActivationPolicy = 0: The application is activated when it becomes frontmost.

        isActive() is not behaving as expected, forcing use of activateWithOptions instead of prompting the user to take action.
        This works for now, but could become a pain point in the future.
        """
        activationResult = app.activateWithOptions_(NSApplicationActivateAllWindows | NSApplicationActivateIgnoringOtherApps)

        if not (activationResult):
            print("Activation failed")
            break

    print("Grabbing a screenshot")
    window = get_window(pid)
    image = ImageWrapper(get_image_from_window(window))

    print("Interpretting the image from ollama")
    payload = {
        "model": "llava",
        "prompt": get_prompt("screenshot_prompt.txt"),
        "stream": False,
        "images": ["{}".format(image.scaled_as_base64())]
    }
    response = requests.post(config.OLLAMA_URL, json=payload)
    responseObj = json.loads(response.text)
    print(responseObj['response'])

    controller = pynput.keyboard.Controller()

    # TODO: Must Have | multiple loops.
    # Loop 1: Capture image, push to a stack or thread-safe variable.
    # Loop 2: Read from stack, inference image. Push instructions to another stack or thread-safe variable.
    # Loop 3: Read from instruction stack and send inputs.
    # TODO: Must Hvae | abstract input to finite set of controller inputs instead of raw key mappings.
    # TODO: Nice to have | read input from user.

    # print("Holding L2")
    # controller.press(pynput.keyboard.KeyCode(char='1'))

    # print("Pressing L1")
    # controller.press(pynput.keyboard.KeyCode(char='2'))
    # controller.release(pynput.keyboard.KeyCode(char='2'))

    # print("Pressing X")
    controller.press(pynput.keyboard.KeyCode(char='\r'))
    controller.release(pynput.keyboard.KeyCode(char='\r'))

    #ssimResult = image.compare_region_ssim("squad_battles-home.png", 63, 25, 260, 56)
    #compare_image_to_screenshot(image, "match-in-progress.png")
    
    # TODO: Next capture screenshot of another menu and compare squad_battles-home to this screenshot. 
    # Consider making it a unit test.

    # Increment statistics
    statistics.count+=1