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
            responseObjText = responseObj['response'].strip(" ")

    return responseObjText