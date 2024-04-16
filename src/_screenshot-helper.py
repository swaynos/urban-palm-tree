from AppKit import NSApplicationActivateAllWindows, NSApplicationActivateIgnoringOtherApps

# urban-palm-tree imports
from app_io import find_app, get_image_from_window
from image import ImageWrapper
from window import get_window 
import config as config
import monitoring as monitoring

# Begin Program
app = find_app(config.APP_NAME)
pid = app.processIdentifier()
statistics = monitoring.Statistics()
screenshotFilename = "screenshots/new-screenshot.png"

# NOTE: This is a temporary script to aid in development
# Run this script and it will capture a screenshot of the active window
# It will loop and overwrite the screenshot

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
    image = get_image_from_window(window)
    image.save(screenshotFilename)

    # Increment statistics
    statistics.count+=1