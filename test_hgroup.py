from h_group import HGroupGameState
from game_state import RANK_CLUE, COLOR_CLUE
from test_functions import check_eq
from test_game_state import create_game_states, get_deck_from_tuples
import datetime as dt


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


def test_all():
    t0 = dt.datetime.now()
    test_clue_focus()
    t1 = dt.datetime.now()
    print(f"All tests passed in {(t1 - t0).total_seconds():.2f}s!")


if __name__ == "__main__":
    test_all()
