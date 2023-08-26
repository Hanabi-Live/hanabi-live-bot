from h_group import HGroupGameState, FinesseNode
from game_state import RANK_CLUE, COLOR_CLUE
from test_functions import check_eq
from test_game_state import create_game_states, get_deck_from_tuples
import datetime as dt
from typing import Dict


def test_clue_focus():
    variant_name = "No Variant"
    # fmt: off
    deck = get_deck_from_tuples(
        [
            (0, 2), (4, 1), (0, 3), (1, 5), (1, 1),
            (4, 4), (3, 2), (2, 2), (4, 1), (2, 1),
            (2, 5), (0, 5), (4, 2), (2, 3), (3, 1),
        ]
    )
    # fmt: on
    STATES_3P = create_game_states(
        3, variant_name, game_state_cls=HGroupGameState, deck=deck
    )
    # p0: y1 [ 4], y5 [ 3], r3 [ 2], p1 [ 1], r2 [ 0]
    # p1: g1 [ 9], p1 [ 8], g2 [ 7], b2 [ 6], p4 [ 5]
    # p2: b1 [14], g3 [13], p2 [12], r5 [11], g5 [10]
    state0: HGroupGameState = STATES_3P[0]
    state1: HGroupGameState = STATES_3P[1]
    state2: HGroupGameState = STATES_3P[2]
    check_eq(state0.get_focus_of_clue(1, orders_touched=[8, 9]), 9)
    check_eq(state1.get_focus_of_clue(1, orders_touched=[8, 9]), 9)
    check_eq(state0.get_chop_order(1), 5)
    check_eq(state1.get_chop_order(1), 5)
    state0.handle_clue(0, 1, RANK_CLUE, 1, [8, 9])
    state1.handle_clue(0, 1, RANK_CLUE, 1, [8, 9])
    check_eq(state0.get_focus_of_clue(1, orders_touched=[5, 8]), 5)
    check_eq(state1.get_focus_of_clue(1, orders_touched=[5, 8]), 5)
    check_eq(state0.get_chop_order(1), 5)
    check_eq(state1.get_chop_order(1), 5)
    state0.handle_clue(0, 1, COLOR_CLUE, 4, [5, 8])
    state1.handle_clue(0, 1, COLOR_CLUE, 4, [5, 8])
    check_eq(state0.get_focus_of_clue(1, orders_touched=[6, 7]), 6)
    check_eq(state1.get_focus_of_clue(1, orders_touched=[6, 7]), 6)
    check_eq(state0.get_chop_order(1), 6)
    check_eq(state1.get_chop_order(1), 6)
    state0.handle_clue(0, 1, RANK_CLUE, 2, [6, 7])
    state1.handle_clue(0, 1, RANK_CLUE, 2, [6, 7])
    check_eq(state0.get_focus_of_clue(1, orders_touched=[7, 9]), 9)
    check_eq(state1.get_focus_of_clue(1, orders_touched=[7, 9]), 9)
    check_eq(state0.get_chop_order(1), None)
    check_eq(state1.get_chop_order(1), None)
    state0.handle_clue(0, 1, COLOR_CLUE, 2, [7, 9])
    state1.handle_clue(0, 1, COLOR_CLUE, 2, [7, 9])

    check_eq(state0.get_focus_of_clue(2, orders_touched=[10, 11]), 10)
    check_eq(state2.get_focus_of_clue(2, orders_touched=[10, 11]), 10)
    check_eq(state0.get_chop_order(2), 10)
    check_eq(state2.get_chop_order(2), 10)
    state0.handle_clue(0, 2, RANK_CLUE, 5, [10, 11])
    state2.handle_clue(0, 2, RANK_CLUE, 5, [10, 11])

    check_eq(state0.get_focus_of_clue(2, orders_touched=[10, 11]), 11)
    check_eq(state2.get_focus_of_clue(2, orders_touched=[10, 11]), 11)
    check_eq(state0.get_chop_order(2), 12)
    check_eq(state2.get_chop_order(2), 12)
    state0.handle_clue(0, 2, RANK_CLUE, 5, [10, 11])
    state2.handle_clue(0, 2, RANK_CLUE, 5, [10, 11])

    check_eq(state0.get_focus_of_clue(2, orders_touched=[10, 13]), 13)
    check_eq(state2.get_focus_of_clue(2, orders_touched=[10, 13]), 13)
    check_eq(state0.get_chop_order(2), 12)
    check_eq(state2.get_chop_order(2), 12)
    state0.handle_clue(0, 2, COLOR_CLUE, 2, [10, 13])
    state2.handle_clue(0, 2, COLOR_CLUE, 2, [10, 13])


def test_get_cards_gotten_from_play_clue():
    variant_name = "No Variant"
    # fmt: off
    deck = get_deck_from_tuples(
        [
            (1, 5), (2, 5), (3, 5), (4, 5),
            (0, 2), (0, 3), (2, 2), (4, 1),
            (2, 4), (2, 3), (3, 2), (3, 1),
            (0, 3), (0, 4), (4, 3), (4, 2)
        ]
    )
    # fmt: on
    STATES: Dict[int, HGroupGameState] = create_game_states(
        4, variant_name, game_state_cls=HGroupGameState, deck=deck
    )
    ss = [1, 1, 1, 0, 0]
    for i in range(4):
        STATES[i].stacks = ss

    # p0: p5 [ 3], b5 [ 2], g5 [ 1], y5 [ 0]
    # p1: p1 [ 7], g2 [ 6], r3 [ 5], r2 [ 4]
    # p2: b1 [11], b2 [10], g3 [ 9], g4 [ 8]
    # p3: p2 [15], p3 [14], 44 [13], r3 [12]

    # direct play clues
    check_eq(STATES[0].get_cards_gotten_from_play_clue(1, RANK_CLUE, 1), {7})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(1, COLOR_CLUE, 4), {7})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(1, RANK_CLUE, 2), {4, 6})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(1, COLOR_CLUE, 0), {4, 5})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(1, COLOR_CLUE, 2), {6})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(2, RANK_CLUE, 1), {11})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(2, COLOR_CLUE, 3), {10, 11})

    for i in range(4):
        STATES[i].super_handle_clue(0, 1, RANK_CLUE, 2, [4, 6])

    STATES[0].print()
    # prompts
    check_eq(STATES[0].get_cards_gotten_from_play_clue(2, RANK_CLUE, 3), {9})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(3, RANK_CLUE, 3), {12, 14})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(3, COLOR_CLUE, 0), {12, 13})

    STATES[0].print()
    # check_eq(STATES[0].get_cards_gotten_from_play_clue(1, RANK_CLUE, 3), {5})

    # simple finesses
    check_eq(STATES[0].get_cards_gotten_from_play_clue(3, RANK_CLUE, 2), {7, 15})
    check_eq(STATES[0].get_cards_gotten_from_play_clue(3, COLOR_CLUE, 4), {7, 14, 15})

    finessable_thru_p1 = {(4, 2), (2, 3)}
    finessable_thru_p2 = {(3, 2), (3, 3)}
    finessable_thru_p12 = {(2, 4)}
    finessable_thru_p13 = {(4, 3), (4, 4)}

    # finessable through p1's hand
    # state2.print()
    # state2.get_finesse_paths(0, COLOR_CLUE, 4, 12).print()


def test_all():
    t0 = dt.datetime.now()
    # test_clue_focus()
    test_get_cards_gotten_from_play_clue()
    t1 = dt.datetime.now()
    print(f"All tests passed in {(t1 - t0).total_seconds():.2f}s!")


if __name__ == "__main__":
    test_all()
