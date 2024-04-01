#from AppKit import NSWindow, CGWindowListCopyWindows
import objc
from ScreenCaptureKit import (
    SCContentFilter,
    SCScreenshotManager,
    SCStreamConfiguration,
    SCShareableContent,
)
import Quartz.CoreGraphics as CG
# https://github.com/ronaldoussoren/pyobjc/issues/590

from AppKit import NSWorkspace

APP_NAME = "Google Chrome"

# Get a list of all open windows
apps = NSWorkspace.sharedWorkspace().runningApplications()

# Iterate over the list of windows
for app in apps:
    if (app.localizedName().lower() == APP_NAME.lower()):
        print(APP_NAME + " is active:" + str(app.isActive()))
        
        #screenshot = CG.CGWindow.imageOfWindow(app)

        # Do something with each application, such as print its name

# Get the window you want to capture
#window = NSWindow(frame=CGRectMake(0, 0, 100, 100))

# Capture the screen of the window using CGWindowListCopyWindows
#image = CGWindowListCopyWindows(window)

# Save the image to a file
#image.save('window_screenshot.png', 'PNG')