import config
import pyscreenshot as ImageGrab

from AppKit import NSRunningApplication, NSWorkspace

def find_app(appName):
    """
    Returns an application object from AppKit if the application with the given name is running, otherwise None.
    
    Args:
        appName (str): The name of the application to search for.
        
    Returns:
        NSRunningApplication or None if no such application is found.
    """
    _app = None
    # Get a list of all running applications
    apps = NSWorkspace.sharedWorkspace().runningApplications()

    # Iterate over the list of windows
    for app in apps:
        # app.bundleIdentifier() can also be used
        if (app.localizedName().lower() == config.APP_NAME.lower()):
            _app = app

    return _app

def get_image_from_window(window):
    """
    Returns an image of the given window, with any unwanted elements removed and resized to 720p resolution (1280x720).
    
    Args:
        window (NSWindow): The window object for which the image should be captured.
        
    Returns:
        A PIL Image object representing the screenshot of the given window.
    """
    deltaX = window.X + window.Width
    deltaY = window.Y + window.Height
    img = ImageGrab.grab(
        backend="mac_screencapture", 
        bbox =(window.X, window.Y, deltaX, deltaY)
    )
    # Remove the top border from the image
    cropped_img = img.crop((0, config.APP_HEADER_HEIGHT, img.width, img.height))
    
    # Resize the image to 720p resolution (1280x720)
    if (config.APP_RESIZE_REQUIRED):
        resized_image = cropped_img.resize((1280, 720))
        final_image = resized_image
    else:
        final_image = cropped_img

    return final_image