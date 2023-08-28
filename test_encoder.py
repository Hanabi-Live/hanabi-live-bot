from encoder import EncoderGameState
from game_state import RANK_CLUE, COLOR_CLUE
from test_functions import check_eq
from test_game_state import create_game_states, get_deck_from_tuples
import datetime as dt
from typing import Dict

import requests

a = requests.get("https://hanab.live/missing-scores/yagami_black/5")
print(a.text)
2 / 0


def test_evaluate_clue_score():
    variant_name = "Omni (5 Suits)"
    # fmt: off
    deck = get_deck_from_tuples(
        [
            (4, 2), (2, 2), (1, 2), (0, 2),
            (4, 3), (2, 3), (1, 3), (0, 3),
            (4, 4), (2, 4), (1, 4), (0, 4),
            (4, 5), (2, 1), (1, 1), (0, 1),
            (4, 1), (1, 1), (2, 1), (0, 1),
        ]
    )
    # fmt: on
    STATES_5P: Dict[int, EncoderGameState] = create_game_states(
        5, variant_name, game_state_cls=EncoderGameState, deck=deck
    )
    STATES_5P[0].stacks = [2, 1, 1, 0, 0]
    print(STATES_5P[0].get_legal_clues())
    a = STATES_5P[0].get_legal_clues()
    for clue_value, clue_type, target_index in a:
        print(
            (clue_value, clue_type, target_index),
            STATES_5P[0].evaluate_clue_score(clue_value, clue_type, target_index),
        )


def test_all():
    t0 = dt.datetime.now()
    test_evaluate_clue_score()
    t1 = dt.datetime.now()
    print(f"All tests passed in {(t1 - t0).total_seconds():.2f}s!")


if __name__ == "__main__":
    test_all()
