import game_state
from game_state import Card, GameState
import numpy as np


def get_random_deck(variant_name: str):
    # usually used for testing purposes
    cards = game_state.get_all_cards_with_multiplicity(variant_name)
    perm = np.random.permutation(cards)
    return [Card(order, x[0], x[1]) for order, x in enumerate(perm)]


def create_game_states(num_players: int, variant_name: str, seed: int):
    np.random.seed(seed)
    player_names = [f"test{x}" for x in range(num_players)]
    states = {
        player_index: GameState(variant_name, player_names, player_index)
        for player_index, _ in enumerate(player_names)
    }
    deck = get_random_deck(variant_name)
    num_cards_per_player = {2: 5, 3: 5, 4: 4, 5: 4, 6: 3}[len(states)]
    order = 0
    for player_index, player_name in enumerate(states):
        for _ in range(num_cards_per_player):
            card = deck.pop(0)
            for player_iterate in states:
                if player_iterate == player_name:
                    states[player_iterate].handle_draw(player_index, order, -1, -1)
                else:
                    states[player_iterate].handle_draw(
                        player_index, order, card.suit_index, card.rank
                    )
            order += 1

    return states


def check_eq(actual, expected):
    assert actual == expected, f"\nExpected: {expected}\nActual: {actual}"


def test_max_num_cards():
    expected_max_num_cards = {
        (suit_index, rank): (
            3
            if (suit_index < 4 and rank == 1)
            else (2 if suit_index < 4 and rank in {2, 3, 4} else 1)
        )
        for suit_index in range(6)
        for rank in range(1, 6)
    }
    state0 = create_game_states(3, "Black & Dark Rainbow (6 Suits)", 20000)[0]
    state1 = create_game_states(3, "Dark Pink & Dark Omni (6 Suits)", 20000)[0]
    state2 = create_game_states(3, "Gray & Cocoa Rainbow (6 Suits)", 20000)[0]
    state3 = create_game_states(3, "Dark Brown & Gray Pink (6 Suits)", 20000)[0]
    state4 = create_game_states(3, "Dark Null & Dark Prism (6 Suits)", 20000)[0]
    for state in [state0, state1, state2, state3, state4]:
        check_eq(state.max_num_cards, expected_max_num_cards)


def test_trash():
    variant_name = "Black (6 Suits)"
    STATES_3P = create_game_states(3, variant_name, 20000)
    state = STATES_3P[0]
    check_eq(state.trash, set())
    state.stacks = [1, 0, 0, 3, 0, 0]
    check_eq(state.trash, {(0, 1), (3, 1), (3, 2), (3, 3)})
    state.discards[(2, 3)] = 2
    check_eq(state.trash, {(0, 1), (3, 1), (3, 2), (3, 3), (2, 4), (2, 5)})
    state.discards[(5, 4)] = 1
    check_eq(state.trash, {(0, 1), (3, 1), (3, 2), (3, 3), (2, 4), (2, 5), (5, 5)})
    state.discards[(5, 2)] = 1
    check_eq(
        state.trash,
        {(0, 1), (3, 1), (3, 2), (3, 3), (2, 4), (2, 5), (5, 3), (5, 4), (5, 5)},
    )


def test_criticals():
    variant_name = "Black (5 Suits)"
    STATES_3P = create_game_states(3, variant_name, 20000)
    state = STATES_3P[0]
    basecrits = {(0, 5), (1, 5), (2, 5), (3, 5), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)}
    check_eq(state.criticals, basecrits)
    state.stacks = [0, 0, 2, 0, 2]
    state.discards = {(2, 1): 2, (2, 4): 1, (1, 2): 1, (3, 1): 2, (4, 5): 1}
    check_eq(
        state.criticals,
        basecrits.union({(1, 2), (2, 4), (3, 1)}).difference({(4, 1), (4, 2), (4, 5)}),
    )
    check_eq(state.non_5_criticals, {(1, 2), (2, 4), (3, 1), (4, 3), (4, 4)})


def test_process_visible_cards():
    variant_name = "Black (6 Suits)"
    STATES_3P = create_game_states(3, variant_name, 20000)
    # p0: p3 [ 4], g1 [ 3], y2 [ 2], k1 [ 1], p1 [ 0]
    # p1: k4 [ 9], y4 [ 8], b3 [ 7], r5 [ 6], k2 [ 5]
    # p2: p2 [14], b1 [13], g3 [12], r2 [11], b5 [10]
    all_cards = game_state.get_all_cards(variant_name)
    for player_index in range(3):
        for candidates in STATES_3P[player_index].our_candidates:
            if player_index == 0:
                check_eq(
                    candidates, all_cards.difference({(0, 5), (3, 5), (5, 2), (5, 4)})
                )
            elif player_index == 1:
                check_eq(candidates, all_cards.difference({(3, 5), (5, 1)}))
            else:
                check_eq(
                    candidates, all_cards.difference({(0, 5), (5, 2), (5, 4), (5, 1)})
                )

    state0 = STATES_3P[0]
    state0.discards[(3, 1)] = 2
    state0.process_visible_cards()
    check_eq(
        state0.our_candidates[0],
        all_cards.difference({(0, 5), (3, 5), (5, 2), (5, 4), (3, 1)}),
    )
    state0.discards[(4, 5)] = 1
    state0.process_visible_cards()
    check_eq(
        state0.our_candidates[0],
        all_cards.difference({(0, 5), (3, 5), (5, 2), (5, 4), (3, 1), (4, 5)}),
    )

    state0.our_candidates[1] = {(5, 1)}
    state0.process_visible_cards()
    check_eq(
        state0.our_candidates[2],
        all_cards.difference({(0, 5), (3, 5), (5, 2), (5, 4), (3, 1), (4, 5), (5, 1)}),
    )
    state0.our_candidates[0] = {(1, 2)}
    state0.our_candidates[2] = {(1, 2)}
    state0.process_visible_cards()
    check_eq(
        state0.our_candidates[3],
        all_cards.difference(
            {(0, 5), (3, 5), (5, 2), (5, 4), (3, 1), (4, 5), (5, 1), (1, 2)}
        ),
    )
    state0.our_candidates[3] = {(1, 5)}
    state0.process_visible_cards()
    check_eq(
        state0.our_candidates[4],
        all_cards.difference(
            {(0, 5), (3, 5), (5, 2), (5, 4), (3, 1), (4, 5), (5, 1), (1, 2), (1, 5)}
        ),
    )

    # test doubletons
    state1 = STATES_3P[1]
    state1.our_candidates[0] = {(3, 3), (5, 4)}
    state1.our_candidates[1] = {(3, 3), (5, 4)}
    state1.process_visible_cards()
    check_eq(state1.our_candidates[3], all_cards.difference({(3, 5), (5, 1)}))

    state1.our_candidates[2] = {(3, 3), (5, 4)}
    state1.process_visible_cards()
    check_eq(
        state1.our_candidates[3],
        all_cards.difference({(3, 5), (5, 1), (3, 3), (5, 4)}),
    )
    state1.our_candidates[0] = {(5, 4)}
    state1.process_visible_cards()
    check_eq(state1.our_candidates[1], {(3, 3)})
    check_eq(state1.our_candidates[2], {(3, 3)})

    # test tripletons
    state2 = STATES_3P[2]
    state2.our_candidates[0] = {(4, 2), (5, 3), (2, 5)}
    state2.our_candidates[1] = {(4, 2), (5, 3), (2, 5)}
    state2.our_candidates[2] = {(4, 2), (5, 3), (2, 5)}
    state2.process_visible_cards()
    check_eq(
        state2.our_candidates[3], all_cards.difference({(0, 5), (5, 2), (5, 4), (5, 1)})
    )

    state2.discards[(4, 2)] = 1
    state2.process_visible_cards()
    check_eq(
        state2.our_candidates[3],
        all_cards.difference({(0, 5), (5, 2), (5, 4), (5, 1), (4, 2), (5, 3), (2, 5)}),
    )


if __name__ == "__main__":
    test_max_num_cards()
    test_trash()
    test_criticals()
    test_process_visible_cards()
    print("All tests passed!")
