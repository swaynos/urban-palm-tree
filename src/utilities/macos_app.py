import ctypes
import utilities.config as config
import logging
import pyscreenshot as ImageGrab
import Quartz
import Quartz.CoreGraphics as CG
from PIL import Image
import numpy as np

from AppKit import NSRunningApplication, NSScreen, NSWorkspace

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

    def get_window(self): 
        if (not self.pid):
            raise ValueError("app/pid must be set, try running find_app before get_window")
        
        logging.debug(f"Looking for window with pid: {self.pid}")
        # TODO: There is a bug if all windows from the application are minimized
        
        # Retrieve window information
        window_list = self._retrieve_window_list_from_quartz()

        matched_windows = []

        for window_info in window_list:
            window_pid = window_info["kCGWindowOwnerPID"]
            if window_pid == self.pid:
                window_width = window_info["kCGWindowBounds"]["Width"]
                window_height = int(window_info["kCGWindowBounds"]["Height"])
                # If any matched windows have non-sensical dimensions
                # don't add them to the matched_windows list
                if (window_height > 270 and window_width > 480):
                    matched_windows.append(window_info)

        matched_windows_length = len(matched_windows)
        if (matched_windows_length > 0):
            if (matched_windows_length > 1):
                largest_dimension_value = 0
                largest_window_index = None
                logging.debug(f"More than one matched window was found, {matched_windows_length} total were found.\nWill return the largest window.") 
                for i, window in enumerate(matched_windows):
                    window_width = window["kCGWindowBounds"]["Width"]
                    window_height = window["kCGWindowBounds"]["Height"]
                    window_x = window["kCGWindowBounds"]["X"]
                    window_y = window["kCGWindowBounds"]["Y"]
                    logging.debug(f"Window {i+1}\n\
                                    Position: {window_x}, {window_y}\n\
                                    Size: {window_width}x{window_height}")
                    if (window_width + window_height) > largest_dimension_value:
                        largest_window_index = i
                        largest_dimension_value = window_width + window_height
                if (largest_window_index is not None):
                    self.window = matched_windows[largest_window_index]
                else:
                    # This error should never happen since we validate the window dimensions earlier
                    raise RuntimeError("Could not find largest window")
            else:
                self.window = matched_windows[0]
            
            window_bounds = self.window["kCGWindowBounds"]

            logging.debug(f"Matched window: {window_bounds}")

            return self.window

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

    def capture_window(self):
        target_window = self.get_window()

        bounds = target_window["kCGWindowBounds"]
        x, y, width, height = int(bounds["X"]), int(bounds["Y"]), int(bounds["Width"]), int(bounds["Height"])

        # TODO: Remove the scaling code after testing on a few devices.
        # Get the scale factor from the main screen (assumes your window is on the main screen)
        # If needed, you can find which screen the window is on and query that screen’s backingScaleFactor
        #scale = NSScreen.mainScreen().backingScaleFactor()
        scale = 1
         # Convert point-based coordinates/size to device pixels
        scaled_x = int(x * scale)
        scaled_y = int(y * scale)
        scaled_w = int(width * scale)
        scaled_h = int(height * scale)

        # Use CGRectMake to define the bounding box
        image_rect = Quartz.CGRectMake(scaled_x, scaled_y, scaled_w, scaled_h)

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
            scaled_w,
            scaled_h,
            8,  # bits per component
            0,  # bytes per row (0 means automatic calculation)
            color_space,
            CG.kCGImageAlphaPremultipliedLast
        )

        # Draw the captured image into the context
        dst_rect = Quartz.CGRectMake(0, 0, scaled_w, scaled_h)
        CG.CGContextDrawImage(context, dst_rect, image_ref)

        # Release the color space
        CG.CGColorSpaceRelease(color_space)

        # Retrieve the resulting image from the context
        result_image = CG.CGBitmapContextCreateImage(context)

        # Convert to a PIL Image
        width = CG.CGImageGetWidth(result_image)
        height = CG.CGImageGetHeight(result_image)
        bitmap_data = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(result_image))
        numpy_array = np.frombuffer(bitmap_data, dtype=np.uint8).reshape((height, width, 4))
        pil_image = Image.fromarray(numpy_array, 'RGBA')
        
        # Resize the image to 540p resolution (960x540) if required
        # TODO: Review the efficiency of buffering the entire bitmap in memory before resizing. 
        # While this approach works, there are a few areas where I could optimize memory usage.
        if config.APP_RESIZE_REQUIRED:
            resized_image = pil_image.resize((960, 540))
            final_image = resized_image
        else:
            final_image = pil_image
        
        return final_image