import utilities.config as config
import logging
import os
import pyscreenshot as ImageGrab
from Xlib import X
from Xlib.display import Display
from Xlib.protocol.event import ClientMessage
from Xlib.protocol.request import QueryTree

class RunningApplication():
    def __init__(self):
         self.window_id = None
    
    def warm_up(self, app_name):
        self.app_name = app_name
        self.find_window_by_name(app_name)
        self.activate_window()

    def activate(self):
        self.activate_window()

    def is_app_active(self) -> bool:
        if (not self.app):
            raise ValueError("app must be set, try running find_app before calling is_app_active_frontmost")
        
        d = Display()

        # Get the currently focused window
        focused_window = d.get_input_focus().focus

        if focused_window == self.window_id:
            return True
        
        return False

    def find_window_by_name(self, window_name):
        display = Display()
        root = display.screen().root
        window_id = None

        # This function recursively searches for a window with the given name
        def search(win):
            nonlocal window_id
            if win.get_wm_name() != None and win.get_wm_name().startswith(window_name):
                logging.debug(f"{win.get_wm_name()} - {win.id} - {win.get_wm_state()}")
                win_state = win.get_wm_state()
                if (win_state):
                    # Will return the first found window with a non-empty state
                    # May return the wrong id if multiple windows are associated with the application
                    window_id = win.id
                    return
            for w in win.query_tree().children:
                if window_id is not None:
                    return
                search(w)

        search(root)
        self.window_id = window_id
        return window_id

    def activate_window(self):
        if (not self.window_id):
            raise ValueError("window_id must be set, try running find_window_by_name before activate_window")
        
        d = Display()
        window = d.create_resource_object('window', self.window_id)

        d.set_input_focus(window, X.RevertToParent, X.CurrentTime)
        window.configure(stack_mode=X.Above)

        d.sync()

    def get_image_from_window(self):
        if (not self.window_id):
            raise ValueError("window_id must be set, try running find_window_by_name before capture. Note: please activate the window.") 

        d = Display()
        window = d.create_resource_object('window', self.window_id)

        # Get window geometry including frame
        geom = window.get_geometry()
        frame = window.query_tree().parent.get_geometry()

        x = frame.x + geom.x
        y = frame.y + geom.y
        width = geom.width
        height = geom.height

        # Adjust for window decorations (frame borders)
        x -= frame.border_width
        y -= frame.border_width
        width += 2 * frame.border_width
        height += 2 * frame.border_width

        # Capture the specific screen area
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))

        
        # Resize the image to 540p resolution (960x540)
        final_image = None
        if (config.APP_RESIZE_REQUIRED):
            resized_image = screenshot.resize((960, 540))
            final_image = resized_image
        else:
            final_image = screenshot

        return final_image