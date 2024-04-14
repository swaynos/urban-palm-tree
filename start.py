from AppKit import NSApplicationActivateAllWindows, NSApplicationActivateIgnoringOtherApps
import pyscreenshot as ImageGrab

# urban-palm-tree imports
from app_io import find_app
from image import ImageWrapper
from window import get_window
import config
import monitoring

# Begin Program
app = find_app(config.APP_NAME)
pid = app.processIdentifier()
statistics = monitoring.Statistics()

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
    deltaX = window.X + window.Width
    deltaY = window.Y + window.Height
    img = ImageGrab.grab(
        backend="mac_screencapture", 
        bbox =(window.X, window.Y, deltaX, deltaY)
    )
    # Remove the top border from the image
    croppedImg = img.crop((0, 56, img.width, img.height))
    
    # Resize the image to 720p resolution (1280x720)
    resized_image = croppedImg.resize((1280, 720))

    # Wrap the image, and run comparisons
    image = ImageWrapper(resized_image)
    ssimResult = image.compare_region_ssim("squad_battles-home.png", 63, 25, 260, 56)
    pixelByPixelResult = image.compare_grayscale_to_template("squad_battles-home.png")
    print("SSIM Result: {}\nPixelByPixelResult: {}\n".format(ssimResult, pixelByPixelResult))
    
    # Increment statistics
    statistics.count+=1