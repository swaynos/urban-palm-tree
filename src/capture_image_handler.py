import asyncio
import logging
from sys import platform
from time import time

import config
from image import ImageWrapper
from shared_resources import clear_oldest_from_lifoqueue, exit_event, screenshots_stack
import monitoring

capture_image_thread_statistics = monitoring.Statistics()

async def capture_image_handler(app):
    """
    In this thread we will capture a screenshot of the desired application and stores it in a global variable for later use.
    It uses the `get_window` and `ImageWrapper` functions from the `app_io` module to grab the window and create an image object.
    The image is then locked with the `latest_screenshot_mutex` lock, ensuring that only one thread can access it at a time.
    """
    logger = logging.getLogger(__name__)
    while(not exit_event.is_set()):
        try:
            logger.debug(f"capture_image_thread: Has looped {capture_image_thread_statistics.count} times. Elapsed time is {capture_image_thread_statistics.get_time()}")
            if platform == "darwin":
                if not app.activate_app():
                    raise RuntimeError("darwin app activation failed")
                app.get_window()
            elif platform == "linux" or platform == "linux2":
                app.activate_window()
            
            logger.debug("capture_image_thread: Grabbing a screenshot")

            image = ImageWrapper(app.get_image_from_window())
            
            if config.SAVE_SCREENSHOTS:
                screenshotFilename = f"{config.SCREENSHOTS_DIR}new-screenshot{time()}.png"
                image._image.save(screenshotFilename)

            if screenshots_stack.full():
                await clear_oldest_from_lifoqueue(screenshots_stack, 8)

            await screenshots_stack.put(image)
            capture_image_thread_statistics.count += 1
            await asyncio.sleep(0)  # Yield control back to the event loop
        except Exception as argument:
            logger.error(argument)