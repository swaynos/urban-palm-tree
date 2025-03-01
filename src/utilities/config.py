# src/utilities/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

# Popular apps include: Moonlight, steamstreamingclient, and Nvidia GeForce Now 
APP_NAME = os.getenv("APP_NAME", "Moonlight")

# App header height is 0 for fullscreen, but it could be 28 or 56 pixels with a menu bar. 
# The exact value depends on DPI settings of the monitor
APP_HEADER_HEIGHT = int(os.getenv("APP_HEADER_HEIGHT", 0))

# Flag - will the window be resized after capture
# Default to false on the assumption CPU is more limited than storage performance.
# TODO: Test this assumption on different hardware.
APP_RESIZE_REQUIRED = os.getenv("APP_RESIZE_REQUIRED", "False").lower() == "true"

# Delay in seconds between loops of capture_image_handler. This allows the user to throttle
# the window focus and image capturing rate. Very useful for debugging.
CAPTURE_IMAGE_DELAY = int(os.getenv("CAPTURE_IMAGE_DELAY", 1))

# Flag - will screenshots be saved
SAVE_SCREENSHOTS = os.getenv("SAVE_SCREENSHOTS", "True").lower() == "true"

# Directory to save screenshots
SCREENSHOTS_DIR = os.getenv("SCREENSHOTS_DIR", "./screenshots/")

# REMOVED, not used for this variation of the codebase
SAVE_SCREENSHOT_RESPONSE = os.getenv("SAVE_SCREENSHOT_RESPONSE", "True").lower() == "true"

# Log level of the application
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

# Ollama URL and model
# REMOVED, not used for this variation of the codebase
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llava")

# secrets
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY')
WANDB_API_KEY= os.getenv('WANDB_API_KEY')
HF_API_KEY= os.getenv('HF_API_KEY')
HF_USERNAME = os.getenv('HF_USERNAME')


# Old configs, not sure if still used.
# This delay will throttle the image capture thread if needed, and avoid overloading the system
CAPTURE_IMAGE_THREAD_DELAY = int(os.getenv('CAPTURE_IMAGE_THREAD_DELAY', 0))

HF_MENU_CLASSIFICATION_PATH = os.getenv('HF_MENU_CLASSIFICATION_PATH', "fc24-in-menu_classification_model")
IN_MENU_CLASSIFICATION_FILENAME = os.getenv('IN_MENU_CLASSIFICATION_FILENAME', "in-menu_classification_model.h5")
HF_MENU_VS_MATCH_PATH = os.getenv('HF_MENU_VS_MATCH_PATH', "fc24-menu_vs_match_model")
MENU_VS_MATCH_FILENAME = os.getenv('MENU_VS_MATCH_FILENAME', "menu_vs_match_model.h5")
HF_SQUAD_SELECTION_PATH = os.getenv('HF_SQUAD_SELECTION_PATH', "fc24-squad_selection_model")
SQUAD_SELECTION_FILENAME = os.getenv('SQUAD_SELECTION_FILENAME', "squad_selection_model.pt")
SQUAD_SELECTION_CONF_THRESHOLD = float(os.getenv('SQUAD_SELECTION_CONF_THRESHOLD', 0.6))

N_LAST_STATES_WEIGHTS = eval(os.getenv('N_LAST_STATES_WEIGHTS', "[1, .8, .6, .4, .2]"))