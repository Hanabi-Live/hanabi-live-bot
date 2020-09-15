from constants import MAX_CLUE_NUM


# This is just a reference;
# for a fully-fledged bot, the game state would need to be more specific
# (e.g. a card object should contain the positive and negative clues that are
# "on" the card)
class GameState:
    replaying_past_actions = True
    clue_tokens = MAX_CLUE_NUM
    players = []
    our_index = -1
    hands = []
    play_stacks = []
    discard_pile = []
    turn = -1
    current_player_index = -1
