import asyncio
import logging
from dispatch import dispatch_async, dispatch_get_main_queue
from concurrent.futures import Future
from time import time

import utilities.config as config
from utilities.image import ImageWrapper
from utilities.macos_app import RunningApplication
import utilities.monitoring as monitoring
from utilities.shared_thread_resources import SharedProgramData

capture_image_thread_statistics = monitoring.Statistics()

async def capture_image_handler(app: RunningApplication, shared_data: SharedProgramData):
    """
    In this thread we will capture a screenshot of the desired application and stores it in a global variable for later use.
    It uses the `get_window` and `ImageWrapper` functions from the `app_io` module to grab the window and create an image object.
    The image is then locked with the `latest_screenshot_mutex` lock, ensuring that only one thread can access it at a time.
    """
    logger = logging.getLogger(__name__)

    while(not shared_data.exit_event.is_set()):
        logger.debug(f"capture_image_thread: Has looped {capture_image_thread_statistics.count} times. Elapsed time is {capture_image_thread_statistics.get_time()}")
        capture_image_thread_statistics.count += 1
        try:
            app.activate()
            
            logger.debug("capture_image_thread: Grabbing a screenshot")
            
            # Capture the image on the main thread
            image = ImageWrapper(app.get_image_from_window())
            
            screenshot_filename = f"{config.SCREENSHOTS_DIR}new-screenshot{time()}.png"
            await image.async_save_image(screenshot_filename)

            # If the collection is full, attempt to remove images from the collection to free space.
            # This needs to be a loop in case there are multiple threads adding screenshots to this
            # collection at once.
            while (shared_data.latest_screenshot.full()):
                await shared_data.latest_screenshot.get()

            await shared_data.latest_screenshot.put(image)
            
            # Even if the value is 0, we need to yield control back to the event loop
            await asyncio.sleep(config.CAPTURE_IMAGE_DELAY) 
        except Exception as argument:
            logger.error(argument)