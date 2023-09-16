from encoder import EncoderGameState
from game_state import RANK_CLUE, COLOR_CLUE, get_all_touched_cards
from test_functions import check_eq
from test_game_state import create_game_states, get_deck_from_tuples
import datetime as dt
from typing import Dict


def give_hat_clue(states: Dict[int, EncoderGameState], giver: int):
    state = states[giver]
    legal_clues = state.get_legal_clues()
    clue_value, clue_type, target_index = list(legal_clues)[-1]
    touched_cards = get_all_touched_cards(clue_type, clue_value, state.variant_name)
    touched_orders = [
        x.order for x in state.hands[target_index] if x.to_tuple() in touched_cards
    ]
    for _state in states.values():
        _state.handle_clue(giver, target_index, clue_type, clue_value, touched_orders)
        _state.turn += 1


def give_clue(
    states: Dict[int, EncoderGameState],
    giver: int,
    clue_type: int,
    clue_value: int,
    target_index: int,
):
    state = states[giver]
    touched_cards = get_all_touched_cards(clue_type, clue_value, state.variant_name)
    touched_orders = [
        x.order for x in state.hands[target_index] if x.to_tuple() in touched_cards
    ]
    for _state in states.values():
        _state.handle_clue(giver, target_index, clue_type, clue_value, touched_orders)
        _state.turn += 1


def discard(states: Dict[int, EncoderGameState], order: int):
    player_index, i = states[0].order_to_index[order]
    another_player = 0 if player_index != 0 else 1
    card_visible = states[another_player].hands[player_index][i]
    assert card_visible.order == order
    for _state in states.values():
        _state.handle_discard(
            player_index, order, card_visible.suit_index, card_visible.rank
        )
        _state.turn += 1


def play(states: Dict[int, EncoderGameState], order: int):
    player_index, i = states[0].order_to_index[order]
    another_player = 0 if player_index != 0 else 1
    card_visible = states[another_player].hands[player_index][i]
    assert card_visible.order == order
    for _state in states.values():
        _state.handle_play(
            player_index, order, card_visible.suit_index, card_visible.rank
        )
        _state.turn += 1


def draw(
    states: Dict[int, EncoderGameState],
    order: int,
    player_index: int,
    suit_index: int,
    rank: int,
):
    for _state in states.values():
        _state.handle_draw(player_index, order, suit_index, rank)


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
    check_eq(STATES_5P[0].evaluate_clue_score(2, RANK_CLUE, 4), 8)
    check_eq(STATES_5P[0].evaluate_clue_score(0, COLOR_CLUE, 4), 9)
    check_eq(STATES_5P[0].evaluate_clue_score(3, COLOR_CLUE, 4), 9)
    check_eq(STATES_5P[0].evaluate_clue_score(4, RANK_CLUE, 2), 8**4)
    check_eq(STATES_5P[0].evaluate_clue_score(2, RANK_CLUE, 2), 8 * 16**3)
    check_eq(STATES_5P[0].evaluate_clue_score(3, COLOR_CLUE, 2), 9 * 15**3)
    check_eq(STATES_5P[0].evaluate_clue_score(2, COLOR_CLUE, 2), 9**2 * 15**2)


def test_superposition():
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

    # p0: r2 [ 3], y2 [ 2], g2 [ 1], o2 [ 0]
    # p1: r3 [ 7], y3 [ 6], g3 [ 5], o3 [ 4]
    # p2: r4 [11], y4 [10], g4 [ 9], o4 [ 8]
    # p3: r1 [15], y1 [14], g1 [13], o5 [12]
    # p4: r1 [19], g1 [18], y1 [17], o1 [16]

    STATES_5P: Dict[int, EncoderGameState] = create_game_states(
        5, variant_name, game_state_cls=EncoderGameState, deck=deck
    )
    give_hat_clue(STATES_5P, 0)
    for i in range(5):
        check_eq(STATES_5P[i].identities_called_to_play, {(0, 1)})

    check_eq(STATES_5P[1].superpositions[7].triggering_orders, {15, 19})
    check_eq(STATES_5P[1].superpositions[7].actual_num_trash, 0)
    check_eq(STATES_5P[1].superpositions[7].get_sp_identities(), {(0, 3)})
    check_eq(STATES_5P[2].superpositions[11].triggering_orders, {15, 19})
    check_eq(STATES_5P[2].superpositions[11].actual_num_trash, 0)
    check_eq(
        STATES_5P[2].superpositions[11].get_sp_identities(), {(0, 4), (2, 5), (4, 4)}
    )
    check_eq(STATES_5P[3].superpositions[15].triggering_orders, {19})
    check_eq(STATES_5P[3].superpositions[15].actual_num_trash, 0)
    check_eq(STATES_5P[3].superpositions[15].get_sp_identities(), {(0, 1)})
    check_eq(STATES_5P[3].our_candidates[-1], {(0, 1)})
    check_eq(STATES_5P[4].superpositions[19].triggering_orders, {15})
    check_eq(STATES_5P[4].superpositions[19].actual_num_trash, 0)
    check_eq(STATES_5P[4].superpositions[19].get_sp_identities(), {(0, 1)})
    check_eq(STATES_5P[4].our_candidates[-1], {(0, 1)})

    give_hat_clue(STATES_5P, 1)
    give_hat_clue(STATES_5P, 2)
    for i in range(5):
        check_eq(STATES_5P[i].identities_called_to_play, {(0, 1), (1, 1), (2, 1)})

    check_eq(STATES_5P[0].superpositions[3].triggering_orders, {14, 18})
    check_eq(STATES_5P[0].superpositions[3].actual_num_trash, 0)
    check_eq(STATES_5P[0].superpositions[3].get_sp_identities(), {(0, 2)})
    check_eq(STATES_5P[0].superpositions[2].triggering_orders, {13, 17})
    check_eq(STATES_5P[0].superpositions[2].actual_num_trash, 0)
    check_eq(STATES_5P[0].superpositions[2].get_sp_identities(), {(1, 2)})
    check_eq(STATES_5P[1].superpositions[6].triggering_orders, {13, 17})
    check_eq(STATES_5P[1].superpositions[6].actual_num_trash, 0)
    check_eq(STATES_5P[1].superpositions[6].get_sp_identities(), {(1, 3)})
    check_eq(STATES_5P[2].superpositions[10].triggering_orders, {14, 18})
    check_eq(STATES_5P[2].superpositions[10].actual_num_trash, 0)
    check_eq(STATES_5P[2].superpositions[10].get_sp_identities(), {(1, 4), (3, 5)})
    check_eq(STATES_5P[3].superpositions[14].triggering_orders, {18})
    check_eq(STATES_5P[3].superpositions[14].actual_num_trash, 0)
    check_eq(
        STATES_5P[3].superpositions[14].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)},
    )

    check_eq(STATES_5P[3].superpositions[13].triggering_orders, {17})
    check_eq(STATES_5P[3].superpositions[13].actual_num_trash, 0)
    check_eq(
        STATES_5P[3].superpositions[13].get_sp_identities(), {(3, 4), (0, 5), (1, 5)}
    )

    check_eq(STATES_5P[4].superpositions[18].triggering_orders, {14})
    check_eq(STATES_5P[4].superpositions[18].actual_num_trash, 0)
    check_eq(
        STATES_5P[4].superpositions[18].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)},
    )
    check_eq(STATES_5P[4].superpositions[17].triggering_orders, {13})
    check_eq(STATES_5P[4].superpositions[17].actual_num_trash, 0)
    check_eq(
        STATES_5P[4].superpositions[17].get_sp_identities(), {(3, 4), (0, 5), (1, 5)}
    )

    discard(STATES_5P, 15)
    for i in range(5):
        check_eq(STATES_5P[i].identities_called_to_play, {(0, 1), (1, 1), (2, 1)})

    check_eq(STATES_5P[4].superpositions[19].triggering_orders, set())
    check_eq(STATES_5P[4].superpositions[19].actual_num_trash, 1)
    check_eq(
        STATES_5P[4].superpositions[19].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)},
    )
    check_eq(STATES_5P[4].our_candidates[-1], {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)})

    play(STATES_5P, 14)
    for i in range(5):
        check_eq(STATES_5P[i].identities_called_to_play, {(0, 1), (2, 1)})

    check_eq(STATES_5P[3].superpositions[13].triggering_orders, set())
    check_eq(STATES_5P[3].superpositions[13].actual_num_trash, 1)
    check_eq(
        STATES_5P[3].superpositions[13].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1)},
    )
    check_eq(STATES_5P[3].our_candidates[1], {(0, 1), (1, 1), (2, 1)})

    play(STATES_5P, 18)
    for i in range(5):
        check_eq(STATES_5P[i].identities_called_to_play, {(0, 1)})

    check_eq(STATES_5P[4].superpositions[17].triggering_orders, set())
    check_eq(STATES_5P[4].superpositions[17].actual_num_trash, 1)
    check_eq(
        STATES_5P[4].superpositions[17].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1)},
    )
    check_eq(STATES_5P[4].our_candidates[1], {(0, 1), (1, 1), (2, 1)})


def test_superposition2():
    # https://hanab.live/replay/1024839
    variant_name = "No Variant"
    # fmt: off
    deck = get_deck_from_tuples(
        [
            (3, 2), (0, 3), (4, 5), (3, 1),
            (4, 3), (4, 4), (1, 5), (1, 1),
            (0, 4), (2, 5), (4, 1), (2, 2),
            (4, 4), (2, 3), (4, 2), (3, 3),
            (2, 4), (2, 1), (2, 1), (2, 1),
        ]
    )
    # fmt: on

    # p0: b1 [ 3], p5 [ 2], r3 [ 1], b2 [ 0]
    # p1: y1 [ 7], y5 [ 6], p4 [ 5], p3 [ 4]
    # p2: g2 [11], p1 [10], g5 [ 9], r4 [ 8]
    # p3: b3 [15], p2 [14], y3 [13], p4 [12]
    # p4: g1 [19], g1 [18], g1 [17], g4 [16]

    STATES_5P: Dict[int, EncoderGameState] = create_game_states(
        5, variant_name, game_state_cls=EncoderGameState, deck=deck
    )

    give_clue(STATES_5P, 0, RANK_CLUE, 3, 1)
    play(STATES_5P, 7)
    draw(STATES_5P, 20, 1, 0, 2)
    give_clue(STATES_5P, 2, RANK_CLUE, 1, 0)
    give_clue(STATES_5P, 3, RANK_CLUE, 4, 2)

    # check
    check_eq(STATES_5P[2].superpositions[11].triggering_orders, {19})
    check_eq(STATES_5P[2].superpositions[11].actual_num_trash, 0)
    check_eq(
        STATES_5P[2].superpositions[11].get_sp_identities(),
        {(2, 2)},
    )
    check_eq(STATES_5P[2].our_candidates[-1], {(2, 2)})
    play(STATES_5P, 17)

    check_eq(STATES_5P[2].superpositions[11].triggering_orders, set())
    check_eq(STATES_5P[2].superpositions[11].actual_num_trash, 0)
    check_eq(
        STATES_5P[2].superpositions[11].get_sp_identities(),
        {(2, 2)},
    )
    check_eq(STATES_5P[2].our_candidates[-1], {(2, 2)})


def test_superposition3():
    # https://hanab.live/shared-replay/1024885
    variant_name = "Prism (5 Suits)"
    # fmt: off
    deck = get_deck_from_tuples(
        [
            (1, 2), (2, 4), (0, 4), (2, 5),
            (0, 1), (2, 3), (1, 2), (2, 2),
            (0, 2), (3, 3), (3, 1), (3, 1),
            (1, 1), (2, 1), (0, 1), (0, 2),
            (0, 3), (2, 3), (0, 1), (4, 1),
        ]
    )
    # fmt: on

    # p0: g5 [ 3], r4 [ 2], b4 [ 1], y2 [ 0]
    # p1: g2 [ 7], y2 [ 6], g3 [ 5], r1 [ 4]
    # p2: b1 [11], b1 [10], b3 [ 9], r2 [ 8]
    # p3: r2 [15], r1 [14], g1 [13], y1 [12]
    # p4: i1 [19], r1 [18], g3 [17], r3 [16]

    STATES_5P: Dict[int, EncoderGameState] = create_game_states(
        5, variant_name, game_state_cls=EncoderGameState, deck=deck
    )

    give_clue(STATES_5P, 0, RANK_CLUE, 1, 3)  # t1
    give_clue(STATES_5P, 1, RANK_CLUE, 4, 0)  # t2
    play(STATES_5P, 11)
    draw(STATES_5P, 20, 2, 4, 4)  # t3
    give_clue(STATES_5P, 3, RANK_CLUE, 2, 0)  # t4
    play(STATES_5P, 19)
    draw(STATES_5P, 21, 4, 1, 1)  # t5
    discard(STATES_5P, 14)

    check_eq(STATES_5P[4].superpositions[18].triggering_orders, set())
    check_eq(STATES_5P[4].superpositions[18].actual_num_trash, 1)
    check_eq(
        STATES_5P[4].superpositions[18].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)},
    )
    check_eq(STATES_5P[2].our_candidates[-2], {(1, 1), (2, 1), (3, 1), (4, 1)})


def test_superposition4():
    # https://hanab.live/shared-replay/1025222

    variant_name = "Prism (5 Suits)"
    # fmt: off
    deck = get_deck_from_tuples(
        [
            (2, 2), (2, 4), (2, 1), (1, 1),
            (0, 3), (3, 3), (0, 1), (0, 4),
            (4, 1), (1, 2), (1, 3), (0, 1),
            (1, 1), (4, 1), (0, 3), (2, 1),
            (1, 4), (0, 4), (1, 3), (1, 2),
        ]
    )
    # fmt: on

    # p0: y1 [ 3], g1 [ 2], g4 [ 1], g2 [ 0]
    # p1: r4 [ 7], r1 [ 6], b3 [ 5], r3 [ 4]
    # p2: r1 [11], y3 [10], y2 [ 9], i1 [ 8]
    # p3: g1 [15], r3 [14], i1 [13], y1 [12]
    # p4: y2 [19], y3 [18], r4 [17], y4 [16]

    STATES_5P: Dict[int, EncoderGameState] = create_game_states(
        5, variant_name, game_state_cls=EncoderGameState, deck=deck
    )
    give_clue(STATES_5P, 0, RANK_CLUE, 1, 1)  # t1

    check_eq(STATES_5P[3].superpositions[15].triggering_orders, {11})
    check_eq(STATES_5P[3].superpositions[15].actual_num_trash, 0)
    check_eq(
        STATES_5P[3].superpositions[15].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)},
    )
    check_eq(STATES_5P[3].our_candidates[-1], {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)})

    play(STATES_5P, 6)
    draw(STATES_5P, 20, 1, 4, 3)  # t2
    check_eq(STATES_5P[3].superpositions[15].triggering_orders, set())
    check_eq(STATES_5P[3].superpositions[15].actual_num_trash, 0)
    check_eq(
        STATES_5P[3].superpositions[15].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)},
    )
    check_eq(STATES_5P[3].our_candidates[-1], {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)})

    discard(STATES_5P, 11)  # t3
    check_eq(STATES_5P[3].superpositions[15].triggering_orders, set())
    check_eq(STATES_5P[3].superpositions[15].actual_num_trash, 0)
    check_eq(
        STATES_5P[3].superpositions[15].get_sp_identities(),
        {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)},
    )
    check_eq(STATES_5P[3].our_candidates[-1], {(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)})


def test_all():
    t0 = dt.datetime.now()
    test_evaluate_clue_score()
    test_superposition()
    test_superposition2()
    test_superposition3()
    test_superposition4()
    t1 = dt.datetime.now()
    print(f"All tests passed in {(t1 - t0).total_seconds():.2f}s!")


if __name__ == "__main__":
    test_all()
