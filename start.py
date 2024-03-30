from AppKit import NSWindow, CGWindowListCopyWindows

# Get the window you want to capture
window = NSWindow(frame=CGRectMake(0, 0, 100, 100))

# Capture the screen of the window using CGWindowListCopyWindows
image = CGWindowListCopyWindows(window)

# Save the image to a file
image.save('window_screenshot.png', 'PNG')
