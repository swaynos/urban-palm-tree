import asyncio
import logging
from sys import platform
from time import time

import config
from image import ImageWrapper
if platform == "darwin":
    from macos_app import RunningApplication
elif platform == "linux" or platform == "linux2":
    from linux_app import RunningApplication
from shared_resources import exit_event, latest_screenshot
import monitoring

capture_image_thread_statistics = monitoring.Statistics()

async def capture_image_handler(app: RunningApplication):
    """
    In this thread we will capture a screenshot of the desired application and stores it in a global variable for later use.
    It uses the `get_window` and `ImageWrapper` functions from the `app_io` module to grab the window and create an image object.
    The image is then locked with the `latest_screenshot_mutex` lock, ensuring that only one thread can access it at a time.
    """
    logger = logging.getLogger(__name__)
    while(not exit_event.is_set()):
        logger.debug(f"capture_image_thread: Has looped {capture_image_thread_statistics.count} times. Elapsed time is {capture_image_thread_statistics.get_time()}")
        capture_image_thread_statistics.count += 1
        try:
            app.activate()
            
            logger.debug("capture_image_thread: Grabbing a screenshot")

            image = ImageWrapper(app.get_image_from_window())
            
            screenshot_filename = f"{config.SCREENSHOTS_DIR}new-screenshot{time()}.png"
            await image.async_save_image(screenshot_filename)

            # If the collection is full, attempt to remove images from the collection to free space.
            # This needs to be a loop in case there are multiple threads adding screenshots to this
            # collection at once.
            while (latest_screenshot.full()):
                await latest_screenshot.get()

            await latest_screenshot.put(image)

            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)