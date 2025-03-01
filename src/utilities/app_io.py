import os

def get_prompt(filename):
    """
    Reads the text from a prompt file and returns it as a string. 
    The prompt file should be located in the "prompts" directory of the current working directory.
    
    Args:
        filename (str): The name of the prompt file to read.
        
    Returns:
        A string containing the text from the given prompt file.
    """
    # Get the absolute path of the prompt file
    prompt_file = os.path.join(os.getcwd(), "prompts", filename)

    # Read the text from the prompt file
    return open(prompt_file, "r").read()