import config
from AppKit import NSRunningApplication, NSWorkspace

def find_app(appName):
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
        if (app.localizedName().lower() == config.APP_NAME.lower()):
            _app = app

    return _app