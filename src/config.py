import os
from dotenv import load_dotenv

# Load environment variables from ./.env and ./.vscode/.env
load_dotenv('.env')
load_dotenv('.vscode/.env')

# secrets
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY')
WANDB_API_KEY= os.getenv('WANDB_API_KEY')
HF_API_KEY= os.getenv('HF_API_KEY')
HF_USERNAME = os.getenv('HF_USERNAME')

# global configs
APP_NAME = os.getenv('APP_NAME', "Chiaki")
APP_HEADER_HEIGHT = int(os.getenv('APP_HEADER_HEIGHT', 0))
APP_RESIZE_REQUIRED = os.getenv('APP_RESIZE_REQUIRED', 'False') == 'True'
SAVE_SCREENSHOTS = os.getenv('SAVE_SCREENSHOTS', 'False') == 'True'
SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', "screenshots/")
SAVE_SCREENSHOT_RESPONSE = os.getenv('SAVE_SCREENSHOT_RESPONSE', 'True') == 'True'
LOG_LEVEL = os.getenv('LOG_LEVEL', "ERROR")
OLLAMA_URL = os.getenv('OLLAMA_URL', "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', "llava")

HF_MENU_CLASSIFICATION_PATH = os.getenv('HF_MENU_CLASSIFICATION_PATH', "fc24-in-menu_classification_model")
IN_MENU_CLASSIFICATION_FILENAME = os.getenv('IN_MENU_CLASSIFICATION_FILENAME', "in-menu_classification_model.h5")
HF_MENU_VS_MATCH_PATH = os.getenv('HF_MENU_VS_MATCH_PATH', "fc24-menu_vs_match_model")
MENU_VS_MATCH_FILENAME = os.getenv('MENU_VS_MATCH_FILENAME', "menu_vs_match_model.h5")
N_LAST_STATES_WEIGHTS = eval(os.getenv('N_LAST_STATES_WEIGHTS', "[1, .8, .6, .4, .2]"))