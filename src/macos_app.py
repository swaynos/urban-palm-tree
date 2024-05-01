import config
import pyscreenshot as ImageGrab
import Quartz

from AppKit import NSRunningApplication, NSWorkspace, NSApplicationActivateAllWindows, NSApplicationActivateIgnoringOtherApps

from window import Window

def activate_app(app: NSRunningApplication):
    # app.isActive: Indicates whether the application is currently frontmost.
    if not (app.isActive()):
        # TODO: Figure out why this spams
        # print("{} is not active, attempting to active. Activation Policy = {}.".format(config.APP_NAME, app.activationPolicy()))
        """
        Activation Policy: https://developer.apple.com/documentation/appkit/nsapplicationactivationpolicy?language=objc
        ActivationPolicy = 0: The application is activated when it becomes frontmost.

        isActive() is not behaving as expected, forcing use of activateWithOptions instead of prompting the user to take action.
        This works for now, but could become a pain point in the future.
        """
        activationResult = app.activateWithOptions_(NSApplicationActivateAllWindows | NSApplicationActivateIgnoringOtherApps)

        if not (activationResult):
            return False
    return True

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
    
    # Resize the image to 540p resolution (960x540)
    if (config.APP_RESIZE_REQUIRED):
        resized_image = cropped_img.resize((960, 540))
        final_image = resized_image
    else:
        final_image = cropped_img

    return final_image

def get_window(pid) -> Window: 
    # TODO: There is a bug if all windows from the application are minimized
    
    # Retrieve window information
    window_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
        Quartz.kCGNullWindowID
    )

    matched_windows = []

    # Iterate through the window list and filter by the app's PID
    for window_info in window_list:
        if window_info["kCGWindowOwnerPID"] == pid:
            # Extract relevant window details (e.g., window ID, title, etc.)
            window = Window()
            window.Height = int(window_info["kCGWindowBounds"]["Height"])
            window.Width = int(window_info["kCGWindowBounds"]["Width"])
            window.X = int(window_info["kCGWindowBounds"]["X"])
            window.Y = int(window_info["kCGWindowBounds"]["Y"])
            matched_windows.append(window)

    if (len(matched_windows) > 0):
        
        # TODO: What if there is more than one window?
        return matched_windows[0]