from enum import Enum

class MenuState(Enum):
    UNKOWN = 1
    HALF_TIME_MENU = 2
    FULL_TIME_MENU = 3
    DIFFICULTY_SELECTION = 4
    SQUAD_BATTLES_OPPONENT_SELECTION = 5
    # Add other menus as needed