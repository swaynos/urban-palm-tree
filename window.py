import Quartz

# window
class Window:
    def __init__(self):
        self.Height = int(0)
        self.Width = int(0)
        self.X = int(0)
        self.Y = int(0)

def get_window(pid):
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
        
        # TODO: What if there is more than one window?
        return matched_windows[0]