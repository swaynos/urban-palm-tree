from AppKit import NSWorkspace, NSApplicationActivateAllWindows, NSApplicationActivateIgnoringOtherApps
import pyscreenshot as ImageGrab
import time

def getApp(appName):
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
        if (app.localizedName().lower() == APP_NAME.lower()):
            _app = app

    return _app

# statistics
class Statistics:
    def __init__(self):
        self.count = 0
        self.start = time.time()
statistics = Statistics()

# Begin Program
APP_NAME = "Google Chrome"
app = getApp(APP_NAME)

# Loop
while(app):
    print("Has looped {} times. Elapsed time is {}".format(statistics.count, time.time() - statistics.start))
    # app.isActive: Indicates whether the application is currently frontmost.
    if not (app.isActive()):
        print("{} is not active, attempting to active. Activation Policy = {}.".format(APP_NAME, app.activationPolicy()))
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
    im = ImageGrab.grab(backend="mac_screencapture") #, bbox =(0, 0, 300, 300))
    """ 
    Performance (note, run in debug mode):
        backend="mac_screencapture"
        88 screenshots over 22.30443811416626s => 4 frames per second
        backend=default
        12 screenshots over 25.30296301841736s => .47 frames per second
    """
    statistics.count+=1
        
        
# Notes
# Create a content filter that includes only the specified window
# content_filter = ScreenCaptureKit.SCContentFilter(display=None,
#                         excludingApplications=[],
#                         exceptingWindows=[])

# for window in windows:



# windowInfo = CGWindowListCopyWindowInfo(pid, Quartz.kCGNullWindowID, Quartz.kCGWindowListOptionAll)
# TODO: Look at this first: https://www.sitepoint.com/quick-tip-controlling-macos-with-python/
# TODO: Go here and figure out what method to use: https://developer.apple.com/documentation/coregraphics/quartz_window_services?language=objc
# window_info = CGWindowListCopyWindowInfo(pid, kCGNullWindowID, kCGWindowListOptionAll)