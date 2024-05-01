import config
import logging
import os
import pyscreenshot as ImageGrab
from Xlib import X, display
from Xlib.display import Display
from Xlib.protocol.event import ClientMessage
from Xlib.protocol.request import QueryTree

class RunningApplication():
    def __init__(self):
         self.window_id = None
    


def find_window_by_name(window_name):
    display = Display()
    root = display.screen().root
    window_id = None

    # This function recursively searches for a window with the given name
    def search(win):
        nonlocal window_id
        if win.get_wm_name() != None and win.get_wm_name().startswith(window_name):
            logging.info(f"{win.get_wm_name()} - {win.id} - {win.get_wm_state()}")
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
    return window_id

def activate_window(window_id):
    d = Display()
    window = d.create_resource_object('window', window_id)

    d.set_input_focus(window, X.RevertToParent, X.CurrentTime)
    window.configure(stack_mode=X.Above)

    d.sync()

def capture_window(window_id):
    d = Display()
    window = d.create_resource_object('window', window_id)

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
    screenshot.save('active_window.png')

wid = find_window_by_name(config.APP_NAME)
activate_window(wid)
capture_window(wid)