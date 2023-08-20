import enum

# Client constants must match the server constants:
# https://github.com/Zamiell/hanabi-live/blob/master/server/src/constants.go


class ACTION(int, enum.Enum):
    PLAY = 0
    DISCARD = 1
    COLOR_CLUE = 2
    RANK_CLUE = 3


MAX_CLUE_NUM = 8
COLOR_CLUE = 0
RANK_CLUE = 1
