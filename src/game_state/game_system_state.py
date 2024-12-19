from enum import Enum

class GameSystemState(Enum):
    """
    Enumeration representing the various states of the game system.

    This is currently a logical combination of GameState, MatchState, and MenuState
    """
    UNKNOWN = 1
    IN_MATCH_OTHER = 2
    IN_MATCH_LIVE = 3
    IN_MATCH_REPLAY = 4
    IN_MATCH_MENU = 5 # full time, or half time menu
    IN_MATCH_POST_MATCH_SUMMARY = 6
    IN_MENU_SQUAD_BATTLES_OPPONENT_SELECTION = 7
    IN_MENU_OTHER = 8
    
    
def get_game_system_states():
    return [state for state in GameSystemState]

def get_game_system_states_str():
    return [str(state.name) for state in GameSystemState]