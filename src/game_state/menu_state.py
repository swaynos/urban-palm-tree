from enum import Enum

class MenuState(Enum):
    FULL_TIME_MENU = 1
    HALF_TIME_MENU = 2
    MENU_POST_MATCH_SUMMARY = 3
    SQUAD_BATTLES_OPPONENT_SELECTION = 4
    UNKNOWN = 5

def get_menu_states():
    return [state for state in MenuState]

def get_menu_states_str():
    return [state.name for state in MenuState]