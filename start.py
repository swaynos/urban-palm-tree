from AppKit import NSWindow, NSWorkspace, NSApplicationActivateAllWindows, NSApplicationActivateIgnoringOtherApps
import pyscreenshot as ImageGrab
import time
import Quartz

# TODO: Move definitions into other files

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
        # app.bundleIdentifier() can also be used
        if (app.localizedName().lower() == APP_NAME.lower()):
            _app = app

    return _app

# window
class Window:
    def __init__(self):
        self.Height = int(0)
        self.Width = int(0)
        self.X = int(0)
        self.Y = int(0)
def getWindow(pid):
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

# statistics
class Statistics:
    def __init__(self):
        self.count = 0
        self.start = time.time()
statistics = Statistics()

# Begin Program
APP_NAME = "Google Chrome"
app = getApp(APP_NAME)
pid = app.processIdentifier()

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
    window = getWindow(pid)
    deltaX = window.X + window.Width
    deltaY = window.Y + window.Height
    im = ImageGrab.grab(
        backend="mac_screencapture", 
        bbox =(window.X, window.Y, deltaX, deltaY)
    )
    """ 
    Performance (note, run in debug mode):
        backend="mac_screencapture"
        88 screenshots over 22.30443811416626s => 4 frames per second
        With reduced screenshot size to just the window:
        139 screenshots over 27.821112632751465 => 4.99 frames per second
        backend=default
        12 screenshots over 25.30296301841736s => .47 frames per second
    """
    statistics.count+=1