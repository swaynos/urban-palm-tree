import logging
import aiohttp
import json

import config

async def infer_image_from_ollama(prompt: str, image_base64: str): 
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "images": [f"{image_base64}"]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(config.OLLAMA_URL, json=payload) as response:
            response_text = await response.text()
            responseObj = json.loads(response_text)
            # Remove whitespace
            responseObjText = responseObj['response'].strip(" ")
            # Clean the response by removing backticks and "json"
            cleaned_response = responseObjText.replace("```json", "").replace("```", "").strip()

    return cleaned_response

async def parse_json_response(logger: logging.Logger, json_str: str):
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
    """
    try:
        json_obj = json.loads(json_str)
        # Validate the object
        match_status = json_obj.get("match-status")
        if match_status not in {"IN-MATCH", "IN-MENU"}:
            logger.error(f"Invalid value for 'match-status': {match_status}. 'match-status' is expected to be one of: IN-MATCH, IN-MENU")
        in_match_status = json_obj.get("in-match-status")
        if in_match_status not in {"NONE", "INSTANT-REPLAY", "LIVE-MATCH"}:
            logger.error(f"Invalid value for 'in-match-status': {in_match_status}. 'in-match-status' must be one of: NONE, INSTANT-REPLAY, LIVE-MATCH")
        minimap = json_obj.get("minimap")
        if minimap not in {"YES", "NO"}:
            logger.error(f"Invalid value for 'minimap': {minimap}. 'minimap' must be one of: YES, NO")
        return json_obj
    except json.JSONDecodeError as jsonDecodeError:
        logger.error(f"Error parsing the json string: {json_str}")
        logger.error(jsonDecodeError)
    except Exception as argument:
        logger.error(f"Error processing the json string: {json_str}")
        logger.error(argument)
    return None