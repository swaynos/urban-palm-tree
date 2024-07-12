from enum import Enum

class GameState(Enum):
    IN_MATCH = 1
    IN_MENU = 2
    

def get_game_states():
    return [state for state in GameState]

def get_game_states_str():
    return [str(state.name) for state in GameState]