from enum import Enum

class MatchState(Enum):
    LIVE_MATCH = 1
    INSTANT_REPLAY = 2
    # Add other match states as needed

def get_match_states_str():
    return [state.name for state in MatchState]