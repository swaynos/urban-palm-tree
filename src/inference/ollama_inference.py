import logging
from typing import Optional
import aiohttp
import json
import re

from utilities import config
from game_state.menu_state import MenuState
from game_state.game_state import get_game_states_str
from game_state.match_state import get_match_states_str
from game_state.menu_state import get_menu_states_str

# Define your response mappings
# TODO: refine these as needed
nlp_response_mappings = {
    r".*main menu.*": "IN-MENU", ##
    r".*selecting opponent.*squad battles.*": "IN-MENU-SQUAD-BATTLES-OPPONENT-SELECT",
    r".*in match.*": "IN-MATCH",
    r".*match in progress.*": "IN-MATCH",
    r".*half-time.*": "IN-MENU-HALF-TIME",
    r".*full-time.*": "IN-MENU-FULL-TIME",
    r'.*"match-status": "IN-MENU".*': "IN-MENU",
    r'.*"in-menu-status": "SQUAD-BATTLES-OPPONENT-SELECTION".*': "IN-MENU-SQUAD-BATTLES-OPPONENT-SELECT"
}

async def infer_image_from_ollama(prompt: str, image_base64: str) -> str: 
    """
    Function to send a prompt and image to an Ollama model for inference
    
    Args:
      prompt (str): Text prompt for the model
      image_base64 (str): Base64 encoded image for inference

    Returns:
      responseObj (str): raw response text from the model
    """
      
    # Construct the payload with model, prompt and image
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "images": [f"{image_base64}"]
    }

    # Send a POST request to the Ollama URL with the payload
    async with aiohttp.ClientSession() as session:
        async with session.post(config.OLLAMA_URL, json=payload) as response:
            response_text = await response.text()
            responseObj = json.loads(response_text)

    return responseObj

async def preprocess_json_string(json_str: str) -> str:
    """
    Preprocess a JSON string to handle common formatting issues.

    Args:
        json_str (str): The JSON string to preprocess.

    Returns:
        str: The preprocessed JSON string.
    """

    # Remove padding whitespace
    json_str = json_str.strip()
    # Remove padding such as ```json and ```
    json_str = re.sub(r'^```json\s*|\s*```$', '', json_str).strip()

    # Regular expression pattern to capture the `in-menu-status` field
    pattern = r'("in-menu-status":\s*)"([^"]+)"\s*\|\s*"([^"]+)"'
    replacement = r'\1["\2", "\3"]'

    # Apply the regular expression substitution
    output_string = re.sub(pattern, replacement, json_str)
    
    return output_string

async def parse_json_response(logger: logging.Logger, json_str: str) -> Optional[dict]:
    """
    Parse a JSON string into an object.

    Args:
        logger (logging.Logger): The logger to use for logging errors.
        json_str (str): The JSON string to parse.

    Returns:
        dict: A dictionary containing the parsed data.

    Raises:
        It will not raise an error on validation failures, but it will log the error and return the parsed object.
        JSONDecodeError: It will not raise an error, but will log the error and return None.
        All other errors: It will log the error and return None

    Note:
        The function will parse the input JSON string, extract specific values based on keys, 
        perform validations, and return a dictionary with the parsed data. 
        Errors encountered during parsing will be logged and the function will return None.
    """
    json_str = await preprocess_json_string(json_str)
    try:
        json_obj = json.loads(json_str)
        json_obj_keys = {key.lower(): value for key, value in json_obj.items()}

        parsed_json = {}

        # match-status
        if "match-status" in json_obj_keys:
            match_status = json_obj.get("match-status", "").upper()
            if match_status not in get_game_states_str():
                logger.warn(f"Invalid match-status: {match_status}, 'match-status' is expected to be one of: {get_game_states_str()}")
            parsed_json["match-status"] = match_status
        else:
            parsed_json["match-status"] = None

        # in-match-status
        if "in-match-status" in json_obj_keys:
            in_match_status = json_obj.get("in-match-status", "").upper()
            if in_match_status and in_match_status not in get_match_states_str():
                logger.warn(f"Invalid in-match-status: {in_match_status}, 'in-match-status' is expected to be one of: {get_match_states_str()}")
            parsed_json["in-match-status"] = in_match_status
        else:
            parsed_json["in-match-status"] = None

        if "in-menu-status" in json_obj_keys:
            in_menu_status = json_obj.get("in-menu-status", "").upper()
            if in_menu_status and in_menu_status not in get_menu_states_str():
                logger.warn(f"Invalid in-menu-status: {in_menu_status}, 'in-menu-status' is expected to be one of: {get_menu_states_str()}")
            parsed_json["in-menu-status"] = in_menu_status
        else:
            parsed_json["in-menu-status"] = MenuState.UNKNOWN.name
        
        # minimap
        if "minimap" in json_obj_keys:
            minimap = json_obj.get("minimap", "").upper()
            if minimap and minimap not in {"YES", "NO"}:
                logger.warn(f"Invalid minimap: {minimap}, 'minimap' is expected to be one of: YES, NO")
            parsed_json["minimap"] = minimap
        else:
            parsed_json["minimap"] = None
        
        return parsed_json
    except json.JSONDecodeError as jsonDecodeError:
        logger.error(f"Error parsing the json string: {json_str}")
        logger.error(jsonDecodeError)
    except Exception as argument:
        logger.error(f"Error processing the json string: {json_str}")
        logger.error(argument)
    return None

async def get_dict_value_nlp_fallback(logger: logging.Logger, json_obj: dict, key: str, response_str:str) -> str:
    """
    Extracts the value associated with a specified key from a dictionary object or falls back to 
    extracting a state from a text response based on predefined patterns.

    Args:
        logger (logging.Logger): The logger to use for logging messages.
        json_obj (dict): The dictionary object from which to extract the value.
        key (str): The key for which to retrieve the value from the dictionary object.
        response_str (str): The text response from which to extract a state if json_obj is None 
        or the specified key is not present in json_obj.

    Returns:
        str: The value associated with the specified key in the dictionary object if present, 
        or the state extracted from the text response based on predefined patterns.

    Notes:
        If the dictionary object is None or the specified key is not present in the object, 
        the function attempts to extract a state from the text response based on predefined patterns. 
        If no matching pattern is found, it returns "UNKNOWN".
    """
    def extract_state_from_text(text):
        # Iterate through predefined patterns to find a matching state
        for pattern, state in nlp_response_mappings.items():
            if re.search(pattern, text, re.IGNORECASE):
                return state
        # Default state if no matching pattern is found
        return "UNKNOWN"
    
    # If the object is empty, attempt to extract a value from the response
    if json_obj is None:
        return extract_state_from_text(response_str)
    # TODO: Im not sure if this could happen since valid json is needed to parse the object. Nor am I confident
    # that the pattern search will work as expected. Try testing some generated edge cases.
    elif json_obj.get(key) is None:
        return extract_state_from_text(response_str)
    
    # Return the value corresponding to the specified key in the object
    return json_obj.get(key)
