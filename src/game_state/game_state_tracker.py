from game_state import GameState, MenuState, MatchState

class GameStateTracker:
    
    def __init__(self):
        self.current_game_state = GameState.IN_MENU
        self.current_menu_state = MenuState.UNKOWN
        self.current_match_state = None

    def set_game_state(self, state):
        # ToDo: provide confidence score, and include debouncing logic if score is low
        # If confidence is high, set state immediately
        # If confidence is low, and the state is changing, wait for a few frames before updating the value
        self.current_game_state = state
        if state == GameState.IN_MENU:
            self.current_match_state = None
        elif state == GameState.IN_MATCH:
            self.current_menu_state = None

    def set_menu_state(self, state: MenuState):
        if self.current_game_state == GameState.IN_MENU:
            self.current_menu_state = state

    def set_match_state(self, state: MatchState):
        if self.current_game_state == GameState.IN_MATCH:
            self.current_match_state = state