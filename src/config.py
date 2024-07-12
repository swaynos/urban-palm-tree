# global static config
APP_NAME= "Chiaki"
APP_HEADER_HEIGHT = 28 #28 or 56, depends on DPI settings and monitor
APP_RESIZE_REQUIRED = False

SCREENSHOT_LOOP_DELAY = 5 # in seconds, how long to delay between screenshot captures
SAVE_SCREENSHOTS = True
SCREENSHOTS_DIR = "screenshots/"
# This will save the screenshot response from Ollama only if the image has been saved
SAVE_SCREENSHOT_RESPONSE = True

LOG_LEVEL = "ERROR"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava"