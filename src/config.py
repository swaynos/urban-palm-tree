# global static config
APP_NAME= "Chiaki"
APP_HEADER_HEIGHT = 28 #28 or 56, depends on DPI settings and monitor
APP_RESIZE_REQUIRED = False

SAVE_SCREENSHOTS = True
SCREENSHOTS_DIR = "screenshots/"
# This will save the screenshot response from Ollama only if the image has been saved
SAVE_SCREENSHOT_RESPONSE = True

LOG_LEVEL = "ERROR"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava"

HF_MENU_CLASSIFICATION_PATH = "bendythepirate/fc24-in-menu_classification_model"
IN_MENU_CLASSIFICATION_FILENAME = "in-menu_classification_model.h5"
HF_MENU_VS_MATCH_PATH = "bendythepirate/fc24-menu_vs_match_model"
MENU_VS_MATCH_FILENAME = "menu_vs_match_model.h5"