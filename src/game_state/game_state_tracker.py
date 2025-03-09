from . import GameState, MenuState, MatchState

class GameStateTracker:
    
    def __init__(self):
        # TODO: Use SharedObject() for thread safety
        self.current_game_state = GameState.IN_MENU
        self.current_menu_state = MenuState.UNKNOWN
        self.current_match_state = None

    def set_game_state(self, state):
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