from constants import MAX_CLUE_NUM


# This is just a reference. For a fully-fledged bot, the game state would need
# to be more specific. (For example, a card object should contain the positive
# and negative clues that are "on" the card.)
class GameState:
    def __init__(self):
        # These must be instance attributes (rather than class attributes) so
        # that each game gets its own lists instead of sharing them.
        self.clue_tokens = MAX_CLUE_NUM
        self.player_names = []
        self.our_player_index = -1
        self.hands = []  # An array containing card objects (dictionaries).
        self.play_stacks = []
        self.discard_pile = []
        self.turn = -1
        self.current_player_index = -1
