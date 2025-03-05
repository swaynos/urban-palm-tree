import utilities.config as config
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
    def _retrieve_window_list_from_quartz(self):
        """
        Queries the Quartz API to retrieve details of all currently visible windows, 
        excluding desktop elements. The returned information includes various attributes 
        such as size, position, owner application, and visibility status.

        Returns:
            list: A list of dictionaries, each representing a window with attributes 
            such as 'kCGWindowOwnerPID' (the process ID of the window's owner) and 
            'kCGWindowBounds' (the bounding rectangle of the window).
        """
        return Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionAll | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID
        )

    def _get_frontmost_app_name(self):
        """
        Retrieves the name of the currently active (frontmost) application window.

        This method queries the list of windows using the Quartz API to find the window that 
        is currently at the topmost layer (layer level of 0). Typically, this window belongs 
        to the application that is currently in focus, and the method returns the name of that 
        application. If no such window is found, the method returns None.

        Returns:
            str: The name of the frontmost application if found; returns None if no window 
            with a layer level of 0 is present or if an error occurs while retrieving the 
            window information.
        """
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID
        )
        for window in window_list:
            if window['kCGWindowLayer'] == 0:
                return window['kCGWindowOwnerName']
            
    def __init__(self):
         self.app: NSRunningApplication = None
         self.app_name = None
         self.pid = None
         self.window = None
    
    def warm_up(self, app_name):
        self.app_name = app_name
        self.find_app(app_name)
        self.activate_app()
        self.get_window()

    def activate(self):
        self.activate_app()

    def is_app_active(self) -> bool:
        if (not self.app):
            raise ValueError("app must be set, try running find_app before calling is_app_active_frontmost")
        active_app = self._get_frontmost_app_name()
        logging.debug(f"Current active application: {active_app}")
        return self.app_name == active_app

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
        logging.debug(f"Looking for app with name: {appName}.\nCurrent list of running applications:")
        for app in apps:
            # app.bundleIdentifier() can also be used
            logging.debug(f"{app.localizedName()} - {app.processIdentifier()}")
            if (app.localizedName().lower() == appName.lower()):
                _app = app

        self.app = _app

        if _app:
            self.pid = _app.processIdentifier()
        else:
            logging.debug(f"No app found")
            self.pid = None

        return _app
    
    def activate_app(self):
        if (not self.app):
            raise ValueError("app must be set, try running find_app before activate_app")

        # app.isActive: Indicates whether the application is currently frontmost.
        if not (self.is_app_active()):
            logging.debug("{} is not active, attempting to activate.".format(config.APP_NAME))
            activationResult = self.app.activateWithOptions_(1)
            if not (activationResult):
                raise RuntimeError("macOS app activation failed")

    def get_window(self) -> Window: 
        if (not self.pid):
            raise ValueError("app/pid must be set, try running find_app before get_window")
        
        logging.debug(f"Looking for window with pid: {self.pid}")
        # TODO: There is a bug if all windows from the application are minimized
        
        # Retrieve window information
        window_list = self._retrieve_window_list_from_quartz()

        matched_windows = []

        logging.debug(matched_windows)
        
        # Iterate through the window list and filter by the app's PID
        for window_info in window_list:
            window_pid = window_info["kCGWindowOwnerPID"]
            if window_pid == self.pid:
                # Extract relevant wwdindow details (e.g., window ID, title, etc.)
                window = Window()
                window.Height = int(window_info["kCGWindowBounds"]["Height"])
                window.Width = int(window_info["kCGWindowBounds"]["Width"])
                window.X = int(window_info["kCGWindowBounds"]["X"])
                window.Y = int(window_info["kCGWindowBounds"]["Y"])

                # If any matched windows have non-sensical dimensions
                # don't add them to the matched_windows list
                if (window.Height > 270 and window.Width > 480):
                    matched_windows.append(window)

        matched_windows_len = len(matched_windows)
        if (matched_windows_len> 0):
            
            if (matched_windows_len > 1):
                largest_dimension_value = 0
                largest_window_index = None
                logging.debug(f"More than one matched window was found, {matched_windows_len} total were found.\nWill return the largest window.") 
                for i, window in enumerate(matched_windows):
                    logging.debug(f"Window {i+1}\nPosition: {window.X}, {window.Y}\nSize: {window.Width}x{window.Height}")
                    if (window.Width * window.Height) > largest_dimension_value:
                        largest_window_index = i
                        largest_dimension_value = window.Width * window.Height
                if (largest_window_index is not None):
                    self.window = matched_windows[largest_window_index]
                else:
                    # This error should never happen since we validate the window dimensions earlier
                    raise RuntimeError("Could not find largest window")
            else:
                self.window = matched_windows[0]
            
            logging.debug(f"Matched window: {self.window}")
            logging.debug(f"Window Position: {self.window.X}, {self.window.Y}")
            logging.debug(f"Window Size: {self.window.Width}x{self.window.Height}")

            return matched_windows[0]

    def get_image_from_window(self):
        """
        Returns an image of the given window, with any unwanted elements removed and resized to 540p resolution (960x540)).
        TODO: set the resized resolution to be configurable.

        Args:
            window (NSWindow): The window object for which the image should be captured.
            
        Returns:
            A PIL Image object representing the screenshot of the given window.
        """
        if (not self.window):
            logging.warn("This object's window is not set, attempting to run get_window")
            self.window = self.get_window()
            if not self.window:
                raise ValueError("Unable to find window.")
        
        deltaX = self.window.X + self.window.Width
        deltaY = self.window.Y + self.window.Height

        # TODO: mac screencapture should support windowid with the 'l' flag.
        #   -l      <windowid> Captures the window with windowid.
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