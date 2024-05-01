import config
import os
import pyscreenshot as ImageGrab
from Xlib import X, display

def Foo():
    app_name = config.APP_NAME

    # Connect to the X server and get the root window
    d = display.Display()
    root = d.screen().root

    # Get the _NET_ACTIVE_WINDOW, which is the window ID of the active window
    net_active_window = d.intern_atom('_NET_ACTIVE_WINDOW')
    window_id = root.get_full_property(net_active_window, X.AnyPropertyType).value[0]

    # Get the active window object
    active_window = d.create_resource_object('window', window_id)

    # Check if the active window's name matches the application name
    if app_name.lower() in active_window.get_wm_name().lower():
        # Your logic to capture the window goes here
        # For example, you can use PIL to take a screenshot
        from PIL import ImageGrab
        ImageGrab.grab().save('screenshot.png', 'PNG')

print(Foo())