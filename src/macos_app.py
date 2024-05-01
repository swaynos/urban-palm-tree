import config
import logging
import pyscreenshot as ImageGrab
import Quartz

from AppKit import NSRunningApplication, NSWorkspace, NSApplicationActivateAllWindows, NSApplicationActivateIgnoringOtherApps

# window
class Window:
    def __init__(self):
        self.Height = int(0)
        self.Width = int(0)
        self.X = int(0)
        self.Y = int(0)

class RunningApplication():
    def __init__(self):
         self.app = None
         self.pid = None
         self.window = None
    
    def find_app(self, appName):
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
            if (app.localizedName().lower() == appName.lower()):
                _app = app

        self.app = _app
        self.pid = app.processIdentifier()
        return _app
    
    def activate_app(self):
        if (not self.app):
            raise ValueError("app must be set, try running find_app before activate_app")

        # app.isActive: Indicates whether the application is currently frontmost.
        if not (self.app.isActive()):
            logging.info("{} is not active, attempting to active. Activation Policy = {}.".format(config.APP_NAME, self.app.activationPolicy()))
            """
            Activation Policy: https://developer.apple.com/documentation/appkit/nsapplicationactivationpolicy?language=objc
            ActivationPolicy = 0: The application is activated when it becomes frontmost.

            TODO: isActive() is not behaving as expected, forcing use of activateWithOptions instead of prompting the user to take action.
            This works for now, but could become a pain point in the future.
            """
            activationResult = self.app.activateWithOptions_(NSApplicationActivateAllWindows | NSApplicationActivateIgnoringOtherApps)

            if not (activationResult):
                return False
        return True

    def get_window(self) -> Window: 
        if (not self.pid):
            raise ValueError("app/pid must be set, try running find_app before get_window")
        
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
            
            if (len(matched_windows) > 1):
                logging.debug("More than one matched window was found. Returning the first window.")

            self.window = matched_windows[0]
            return matched_windows[0]


    def get_image_from_window(self):
        """
        Returns an image of the given window, with any unwanted elements removed and resized to 720p resolution (1280x720).
        
        Args:
            window (NSWindow): The window object for which the image should be captured.
            
        Returns:
            A PIL Image object representing the screenshot of the given window.
        """
        if (not self.window):
            raise ValueError("window must be set, try running get_window before get_image_from_window")
        
        deltaX = self.window.X + self.window.Width
        deltaY = self.window.Y + self.window.Height
        img = ImageGrab.grab(
            backend="mac_screencapture", 
            bbox =(self.window.X, self.window.Y, deltaX, deltaY)
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