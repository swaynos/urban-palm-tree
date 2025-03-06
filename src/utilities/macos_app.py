import ctypes
import utilities.config as config
import logging
import pyscreenshot as ImageGrab
import Quartz
import Quartz.CoreGraphics as CG
from PIL import Image
import numpy as np

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

    def capture_window(self):
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID
        )

        target_window = None
        for window in window_list:
            if window["kCGWindowOwnerPID"] == self.pid:
                target_window = window
                break

        if not target_window:
            raise ValueError("Window not found for PID:", self.pid)

        bounds = target_window["kCGWindowBounds"]
        x, y, width, height = int(bounds["X"]), int(bounds["Y"]), int(bounds["Width"]), int(bounds["Height"])

        # Use CGRectMake to define the bounding box
        image_rect = Quartz.CGRectMake(x, y, width, height)

        # Capture the window as a CGImageRef
        image_ref = Quartz.CGWindowListCreateImage(
            image_rect,
            Quartz.kCGWindowListOptionIncludingWindow,
            target_window["kCGWindowNumber"],
            Quartz.kCGWindowImageBoundsIgnoreFraming
        )

        if not image_ref:
            raise RuntimeError("Failed to capture image.")

        # Create a bitmap context
        color_space = CG.CGColorSpaceCreateDeviceRGB()
        context = CG.CGBitmapContextCreate(
            None,
            int(image_rect.size.width),
            int(image_rect.size.height),
            8,  # bits per component
            0,  # bytes per row (0 means automatic calculation)
            color_space,
            CG.kCGImageAlphaPremultipliedLast
        )

        # Draw the image onto the context
        CG.CGContextDrawImage(context, image_rect, image_ref)

        # Release the color space
        CG.CGColorSpaceRelease(color_space)

        # Retrieve the resulting image from the context
        result_image = CG.CGBitmapContextCreateImage(context)

        # Convert to a PIL Image
        width = CG.CGImageGetWidth(result_image)
        height = CG.CGImageGetHeight(result_image)
        bits_per_component = 8
        bytes_per_row = width * 4
        bitmap_data = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(result_image))
        numpy_array = np.frombuffer(bitmap_data, dtype=np.uint8).reshape((height, width, 4))
        pil_image = Image.fromarray(numpy_array, 'RGBA')
        
        return pil_image