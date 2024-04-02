#from AppKit import NSWindow, CGWindowListCopyWindows
import objc
from ScreenCaptureKit import (
    SCContentFilter,
    SCScreenshotManager,
    SCStreamConfiguration,
    SCShareableContent,
)
from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionAll
import Quartz.CoreGraphics as CG
# TODO: Actually read this
# https://github.com/ronaldoussoren/pyobjc/issues/590

from AppKit import NSWorkspace

APP_NAME = "Google Chrome"

# Get a list of all open windows
apps = NSWorkspace.sharedWorkspace().runningApplications()

# Iterate over the list of windows
for app in apps:
    if (app.localizedName().lower() == APP_NAME.lower()):
        # active: Indicates whether the application is currently frontmost.
        # hidden: Indicates whether the application is currently hidden.
        print(APP_NAME + " is hidden : " + str(app.isHidden()))
        if (not app.isHidden()):
            pid = app.processIdentifier()
            # TODO: Look at this first: https://www.sitepoint.com/quick-tip-controlling-macos-with-python/
            # TODO: Go here and figure out what method to use: https://developer.apple.com/documentation/coregraphics/quartz_window_services?language=objc
            window_info = CGWindowListCopyWindowInfo(pid, kCGNullWindowID, kCGWindowListOptionAll)
            
        #screenshot = CG.CGWindow.imageOfWindow(app)

        # Do something with each application, such as print its name

# Get the window you want to capture
#window = NSWindow(frame=CGRectMake(0, 0, 100, 100))

# Capture the screen of the window using CGWindowListCopyWindows
#image = CGWindowListCopyWindows(window)

# Save the image to a file
#image.save('window_screenshot.png', 'PNG')