import game_state
import datetime as dt


def all_suit(suit_index):
    return {(suit_index, i) for i in range(1, 6)}


def all_rank(rank, suit_indices):
    return {(suit_index, rank) for suit_index in suit_indices}


def check_eq(actual, expected):
    assert actual == expected, f"\nExpected: {expected}\nActual: {actual}"


def run_simple_test(fn, tests):
    for input, exp in tests.items():
        act = fn(input) if not isinstance(input, tuple) else fn(*input)
        fn_name = fn.__name__
        assert act == exp, f"{fn_name}\nInput: {input}\nExpected: {exp}\nActual: {act}"
    print(f"{len(tests)} tests for {fn_name} passed!")


def test_get_available_rank_clues():
    tests = {
        "Light-Pink-Fives & Light Pink (5 Suits)": [1, 2, 3, 4],
        "Omni-Fives (5 Suits)": [1, 2, 3, 4],
        "Deceptive-Fives & Omni (5 Suits)": [1, 2, 3, 4],
        "Muddy-Rainbow-Fives & Rainbow (5 Suits)": [1, 2, 3, 4],
        "Brown-Fives & Null (5 Suits)": [1, 2, 3, 4],
        "Null-Fives (5 Suits)": [1, 2, 3, 4],
        "Pink-Fives & Pink (5 Suits)": [1, 2, 3, 4],
        "Rainbow-Fives & Prism (5 Suits)": [1, 2, 3, 4, 5],
        "White-Fives & Prism (5 Suits)": [1, 2, 3, 4, 5],
        "Brown-Ones & White (5 Suits)": [2, 3, 4, 5],
        "Pink-Ones & Omni (5 Suits)": [2, 3, 4, 5],
        "Null-Ones & Muddy Rainbow (5 Suits)": [2, 3, 4, 5],
        "Omni-Ones & White (5 Suits)": [2, 3, 4, 5],
        "Muddy-Rainbow-Ones & Omni (5 Suits)": [2, 3, 4, 5],
        "Deceptive-Ones (5 Suits)": [2, 3, 4, 5],
        "Light-Pink-Ones & Muddy Rainbow (5 Suits)": [2, 3, 4, 5],
        "White-Ones & Light Pink (5 Suits)": [1, 2, 3, 4, 5],
        "Rainbow-Ones & Omni (5 Suits)": [1, 2, 3, 4, 5],
        "Odds and Evens & Rainbow (5 Suits)": [1, 2],
        "Odds and Evens (5 Suits)": [1, 2],
        "No Variant": [1, 2, 3, 4, 5],
        "6 Suits": [1, 2, 3, 4, 5],
        "Black (6 Suits)": [1, 2, 3, 4, 5],
        "Pink (6 Suits)": [1, 2, 3, 4, 5],
        "Brown (6 Suits)": [1, 2, 3, 4, 5],
        "Pink & Brown (6 Suits)": [1, 2, 3, 4, 5],
        "Dark Pink & Gray (6 Suits)": [1, 2, 3, 4, 5],
        "Black & Pink (5 Suits)": [1, 2, 3, 4, 5],
        "Pink & Cocoa Rainbow (5 Suits)": [1, 2, 3, 4, 5],
        "Omni & Dark Brown (5 Suits)": [1, 2, 3, 4, 5],
        "Omni (5 Suits)": [1, 2, 3, 4, 5],
        "Rainbow & Omni (5 Suits)": [1, 2, 3, 4, 5],
        "Rainbow & White (4 Suits)": [1, 2, 3, 4, 5],
        "Null & Muddy Rainbow (4 Suits)": [1, 2, 3, 4, 5],
        "White & Null (3 Suits)": [1, 2, 3, 4, 5],
        "Omni & Muddy Rainbow (3 Suits)": [1, 2, 3, 4, 5],
        "Valentine Mix (5 Suits)": [1, 2, 3, 4, 5],
        "Valentine Mix (6 Suits)": [1, 2, 3, 4, 5],
        "Special Mix (5 Suits)": [1, 2, 3, 4, 5],
        "Special Mix (6 Suits)": [1, 2, 3, 4, 5],
    }
    run_simple_test(game_state.get_available_rank_clues, tests)


def test_get_available_color_clues():
    tests = {
        "No Variant": ["Red", "Yellow", "Green", "Blue", "Purple"],
        "6 Suits": ["Red", "Yellow", "Green", "Blue", "Purple", "Teal"],
        "Black (6 Suits)": ["Red", "Yellow", "Green", "Blue", "Purple", "Black"],
        "Pink (6 Suits)": ["Red", "Yellow", "Green", "Blue", "Purple", "Pink"],
        "Brown (6 Suits)": ["Red", "Yellow", "Green", "Blue", "Purple", "Brown"],
        "Pink & Brown (6 Suits)": ["Red", "Yellow", "Green", "Blue", "Pink", "Brown"],
        "Dark Pink & Gray (6 Suits)": ["Red", "Yellow", "Green", "Blue", "Dark Pink"],
        "Black & Pink (5 Suits)": ["Red", "Green", "Blue", "Black", "Pink"],
        "Pink & Cocoa Rainbow (5 Suits)": ["Red", "Green", "Blue", "Pink"],
        "Omni & Dark Brown (5 Suits)": ["Red", "Green", "Blue", "Dark Brown"],
        "Omni (5 Suits)": ["Red", "Yellow", "Green", "Blue"],
        "Rainbow & Omni (5 Suits)": ["Red", "Green", "Blue"],
        "Rainbow & White (4 Suits)": ["Red", "Blue"],
        "Null & Muddy Rainbow (4 Suits)": ["Red", "Blue"],
        "White & Null (3 Suits)": ["Red"],
        "Omni & Muddy Rainbow (3 Suits)": ["Red"],
        "Valentine Mix (5 Suits)": ["Red", "Pink"],
        "Valentine Mix (6 Suits)": ["Red", "Pink"],
        "Special Mix (5 Suits)": ["Black", "Pink", "Brown"],
        "Special Mix (6 Suits)": ["Black", "Pink", "Brown"],
        "Ambiguous (6 Suits)": ["Red", "Green", "Blue"],
        "Very Ambiguous (6 Suits)": ["Red", "Blue"],
        "Extremely Ambiguous (6 Suits)": ["Blue"],
        "Ambiguous & Black (5 Suits)": ["Red", "Blue", "Black"],
        "Extremely Ambiguous & Pink (6 Suits)": ["Blue", "Pink"],
        "Holiday Mix (5 Suits)": ["Green", "Blue", "Dark Pink"],
        "Matryoshka (6 Suits)": ["Red", "Yellow", "Green", "Blue", "Purple", "Teal"],
        "Matryoshka & White (6 Suits)": ["Red", "Yellow", "Green", "Blue", "Purple"],
        "Matryoshka & Dark Rainbow (5 Suits)": ["Red", "Yellow", "Green", "Blue"],
        "Matryoshka & Prism (4 Suits)": ["Red", "Yellow", "Green"],
        "Matryoshka & Light Pink (3 Suits)": ["Red", "Yellow"],
        # "Dual-Color (6 Suits)": ["Red", "Yellow", "Blue", "Purple"],
        "Dual-Color (5 Suits)": ["Red", "Yellow", "Green", "Blue", "Purple"],
        "Dual-Color & Dark Brown (6 Suits)": [
            "Red",
            "Yellow",
            "Green",
            "Blue",
            "Purple",
            "Dark Brown",
        ],
        "Dual-Color (3 Suits)": ["Red", "Yellow", "Blue"],
        "Dual-Color & Pink (4 Suits)": ["Red", "Yellow", "Blue", "Pink"],
        "Dual-Color Mix": ["Red", "Yellow", "Blue", "Black"],
        "Ambiguous & Dual-Color": ["Red", "Yellow", "Blue"],
    }
    run_simple_test(game_state.get_available_color_clues, tests)


def test_get_all_touched_cards():
    # fmt: off
    C, R = game_state.COLOR_CLUE, game_state.RANK_CLUE
    tests = {
        (C, 1, "No Variant"): all_suit(1),
        (C, 5, "Black (6 Suits)"): all_suit(5),
        (C, 2, "Rainbow (4 Suits)"): all_suit(2).union(all_suit(3)),
        (C, 2, "Dark Rainbow (5 Suits)"): all_suit(2).union(all_suit(4)),
        (C, 3, "Pink (4 Suits)"): all_suit(3),
        (C, 4, "Dark Pink (5 Suits)"): all_suit(4),
        (C, 2, "White (4 Suits)"): all_suit(2),
        (C, 2, "Gray (5 Suits)"): all_suit(2),
        (C, 3, "Brown (4 Suits)"): all_suit(3),
        (C, 4, "Dark Brown (5 Suits)"): all_suit(4),
        (C, 2, "Cocoa Rainbow (5 Suits)"): all_suit(2).union(all_suit(4)),
        (C, 2, "Omni (5 Suits)"): all_suit(2).union(all_suit(4)),
        (C, 2, "Dark Omni (5 Suits)"): all_suit(2).union(all_suit(4)),
        (C, 2, "Null (5 Suits)"): all_suit(2),
        (C, 2, "Dark Null (5 Suits)"): all_suit(2),
        (C, 1, "Rainbow & Omni (4 Suits)"): all_suit(1).union(all_suit(2)).union(all_suit(3)),
        (C, 0, "Null & Prism (5 Suits)"): all_suit(0).union({(4, 1), (4, 4)}),
        (C, 1, "Null & Prism (5 Suits)"): all_suit(1).union({(4, 2), (4, 5)}),
        (C, 2, "Null & Prism (5 Suits)"): all_suit(2).union({(4, 3)}),
        (C, 0, "Dark Prism (6 Suits)"): all_suit(0).union({(5, 1)}),
        (C, 1, "Dark Prism (6 Suits)"): all_suit(1).union({(5, 2)}),
        (C, 2, "Dark Prism (6 Suits)"): all_suit(2).union({(5, 3)}),
        (C, 3, "Dark Prism (6 Suits)"): all_suit(3).union({(5, 4)}),
        (C, 4, "Dark Prism (6 Suits)"): all_suit(4).union({(5, 5)}),
        (C, 1, "Rainbow-Ones & Omni (5 Suits)"): all_suit(1).union(all_suit(4)).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Rainbow-Ones & White (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Rainbow-Ones & Light Pink (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Rainbow-Ones & Gray (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Rainbow-Ones & Gray Pink (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Muddy-Rainbow-Ones & Omni (5 Suits)"): all_suit(1).union(all_suit(4)).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Muddy-Rainbow-Ones & White (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Muddy-Rainbow-Ones & Light Pink (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Muddy-Rainbow-Ones & Dark Null (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Omni-Ones & Omni (5 Suits)"): all_suit(1).union(all_suit(4)).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Omni-Ones & White (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Omni-Ones & Light Pink (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "Omni-Ones & Dark Null (5 Suits)"): all_suit(1).union({(0, 1), (2, 1), (3, 1)}),
        (C, 1, "White-Ones & Light Pink (5 Suits)"): all_suit(1).difference({(1, 1)}),
        (C, 1, "White-Ones & Rainbow (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "White-Ones & Muddy Rainbow (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "White-Ones & Omni (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "Light-Pink-Ones & Light Pink (5 Suits)"): all_suit(1).difference({(1, 1)}),
        (C, 1, "Light-Pink-Ones & Rainbow (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "Light-Pink-Ones & Muddy Rainbow (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "Light-Pink-Ones & Omni (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "Null-Ones & Light Pink (5 Suits)"): all_suit(1).difference({(1, 1)}),
        (C, 1, "Null-Ones & Rainbow (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "Null-Ones & Muddy Rainbow (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 1, "Null-Ones & Omni (5 Suits)"): all_suit(1).union(all_suit(4)).difference({(1, 1)}),
        (C, 0, "Ambiguous (6 Suits)"): all_suit(0).union(all_suit(1)),
        (C, 1, "Ambiguous (6 Suits)"): all_suit(2).union(all_suit(3)),
        (C, 2, "Ambiguous (6 Suits)"): all_suit(4).union(all_suit(5)),
        (C, 0, "Very Ambiguous (6 Suits)"): all_suit(0).union(all_suit(1)).union(all_suit(2)),
        (C, 1, "Very Ambiguous (6 Suits)"): all_suit(3).union(all_suit(4)).union(all_suit(5)),
        (C, 0, "Extremely Ambiguous (6 Suits)"): {x for i in range(6) for x in all_suit(i)},
        (C, 0, "Holiday Mix (5 Suits)"): all_suit(1),
        (C, 1, "Holiday Mix (5 Suits)"): all_suit(3).union(all_suit(4)),
        (C, 2, "Holiday Mix (5 Suits)"): all_suit(0),
        (C, 0, "Holiday Mix (6 Suits)"): all_suit(1),
        (C, 1, "Holiday Mix (6 Suits)"): all_suit(2),
        (C, 2, "Holiday Mix (6 Suits)"): all_suit(4).union(all_suit(5)),

        # TODO: confirm deceptive + funnels/chimneys
        (R, 2, "No Variant"): all_rank(2, range(5)),
        (R, 2, "Rainbow (4 Suits)"): all_rank(2, range(4)),
        (R, 2, "Pink (4 Suits)"): all_rank(2, range(4)).union(all_suit(3)),
        (R, 2, "Dark Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "White (4 Suits)"): all_rank(2, range(4)),
        (R, 2, "Brown (4 Suits)"): all_rank(2, range(3)),
        (R, 2, "Dark Brown (5 Suits)"): all_rank(2, range(4)),
        (R, 2, "Cocoa Rainbow (5 Suits)"): all_rank(2, range(4)),
        (R, 2, "Light Pink (4 Suits)"): all_rank(2, range(4)).union(all_suit(3)),
        (R, 2, "Gray Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Omni (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Dark Omni (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Null (5 Suits)"): all_rank(2, range(4)),
        (R, 2, "Dark Null (5 Suits)"): all_rank(2, range(4)),
        (R, 2, "Rainbow & Omni (4 Suits)"): all_rank(2, range(3)).union(all_suit(3)),
        (R, 2, "Pink-Ones & Omni (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).union(all_suit(4)),
        (R, 2, "Pink-Ones & Brown (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Pink-Ones & Muddy Rainbow (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Pink-Ones & Dark Brown (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Pink-Ones & Cocoa Rainbow (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Light-Pink-Ones & Omni (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).union(all_suit(4)),
        (R, 2, "Light-Pink-Ones & Brown (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Light-Pink-Ones & Muddy Rainbow (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Light-Pink-Ones & Dark Null (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Omni-Ones & Omni (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).union(all_suit(4)),
        (R, 2, "Omni-Ones & Brown (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Omni-Ones & Muddy Rainbow (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Omni-Ones & Dark Null (5 Suits)"): all_rank(2, range(4)).union(all_rank(1, range(4))).difference({(4, 1)}),
        (R, 2, "Brown-Ones & Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Brown-Ones & Light Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Brown-Ones & Omni (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Muddy-Rainbow-Ones & Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Muddy-Rainbow-Ones & Light Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Muddy-Rainbow-Ones & Omni (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Null-Ones & Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Null-Ones & Light Pink (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 2, "Null-Ones & Omni (5 Suits)"): all_rank(2, range(4)).union(all_suit(4)),
        (R, 0, "Odds and Evens (5 Suits)"): all_rank(2, range(5)).union(all_rank(4, range(5))),
        (R, 1, "Odds and Evens (5 Suits)"): all_rank(1, range(5)).union(all_rank(3, range(5))).union(all_rank(5, range(5))),
        (R, 0, "Odds and Evens & Pink (5 Suits)"): all_rank(2, range(5)).union(all_rank(4, range(5))).union(all_suit(4)),
        (R, 1, "Odds and Evens & Pink (5 Suits)"): all_rank(1, range(5)).union(all_rank(3, range(5))).union(all_rank(5, range(5))).union(all_suit(4)),
        (R, 2, "Deceptive-Ones & Null (6 Suits)"): all_rank(2, range(5)).union({(0, 1), (4, 1)}),
        (R, 3, "Deceptive-Ones (6 Suits)"): all_rank(3, range(6)).union({(1, 1), (5, 1)}),
        (R, 4, "Deceptive-Ones & Muddy Rainbow (6 Suits)"): all_rank(4, range(5)).union({(2, 1)}),
        (R, 5, "Deceptive-Ones & Null (6 Suits)"): all_rank(5, range(5)).union({(3, 1)}),
        (R, 2, "Deceptive-Ones (5 Suits)"): all_rank(2, range(5)).union({(0, 1), (4, 1)}),
        (R, 3, "Deceptive-Ones (5 Suits)"): all_rank(3, range(5)).union({(1, 1)}),
        (R, 4, "Deceptive-Ones (5 Suits)"): all_rank(4, range(5)).union({(2, 1)}),
        (R, 5, "Deceptive-Ones (5 Suits)"): all_rank(5, range(5)).union({(3, 1)}),
        (R, 1, "Deceptive-Fives & Dark Null (6 Suits)"): all_rank(1, range(5)).union({(0, 5), (4, 5)}),
        (R, 2, "Deceptive-Fives (6 Suits)"): all_rank(2, range(6)).union({(1, 5), (5, 5)}),
        (R, 3, "Deceptive-Fives & Dark Brown (6 Suits)"): all_rank(3, range(5)).union({(2, 5)}),
        (R, 4, "Deceptive-Fives & Cocoa Rainbow (6 Suits)"): all_rank(4, range(5)).union({(3, 5)}),
        (R, 1, "Deceptive-Fives (5 Suits)"): all_rank(1, range(5)).union({(0, 5), (4, 5)}),
        (R, 2, "Deceptive-Fives (5 Suits)"): all_rank(2, range(5)).union({(1, 5)}),
        (R, 3, "Deceptive-Fives (5 Suits)"): all_rank(3, range(5)).union({(2, 5)}),
        (R, 4, "Deceptive-Fives (5 Suits)"): all_rank(4, range(5)).union({(3, 5)}),
        (R, 1, "Funnels (5 Suits)"): {x for i in {1} for x in all_rank(i, range(5))},
        (R, 2, "Funnels (5 Suits)"): {x for i in {1, 2} for x in all_rank(i, range(5))},
        (R, 3, "Funnels (5 Suits)"): {x for i in range(1, 4) for x in all_rank(i, range(5))},
        (R, 4, "Funnels (5 Suits)"): {x for i in range(1, 5) for x in all_rank(i, range(5))},
        (R, 5, "Funnels (5 Suits)"): {x for i in range(1, 6) for x in all_rank(i, range(5))},
        (R, 1, "Chimneys (5 Suits)"): {x for i in range(1, 6) for x in all_rank(i, range(5))},
        (R, 2, "Chimneys (5 Suits)"): {x for i in range(2, 6) for x in all_rank(i, range(5))},
        (R, 3, "Chimneys (5 Suits)"): {x for i in range(3, 6) for x in all_rank(i, range(5))},
        (R, 4, "Chimneys (5 Suits)"): {x for i in {4, 5} for x in all_rank(i, range(5))},
        (R, 5, "Chimneys (5 Suits)"): {x for i in {5} for x in all_rank(i, range(5))},
    }
    run_simple_test(game_state.get_all_touched_cards, tests)
    # fmt: on


def test_is_brownish_pinkish():
    tests = {
        "No Variant": False,
        "Black (5 Suits)": False,
        "Prism (5 Suits)": False,
        "Dark Prism (5 Suits)": False,
        "Black & Dark Prism (6 Suits)": False,
        "Rainbow (5 Suits)": False,
        "Dark Rainbow (5 Suits)": False,
        "White (5 Suits)": False,
        "Gray (5 Suits)": False,
        "Brown (6 Suits)": True,
        "Dark Brown (6 Suits)": True,
        "Gray & Dark Brown (6 Suits)": True,
        "Pink (6 Suits)": True,
        "Dark Pink (6 Suits)": True,
        "Light Pink (6 Suits)": True,
        "Gray Pink (6 Suits)": True,
        "Muddy Rainbow (6 Suits)": True,
        "Cocoa Rainbow (6 Suits)": True,
        "Omni (6 Suits)": True,
        "Dark Omni (6 Suits)": True,
        "Null (6 Suits)": True,
        "Dark Null (6 Suits)": True,
        "Special Mix (5 Suits)": True,
        "Special Mix (6 Suits)": True,
        "Valentine Mix (5 Suits)": True,
        "Valentine Mix (6 Suits)": True,
        "White-Ones (6 Suits)": False,
        "Rainbow-Ones (6 Suits)": False,
        "Pink-Ones (6 Suits)": True,
        "Brown-Ones (6 Suits)": True,
        "Null-Ones (6 Suits)": True,
        "Deceptive-Ones (6 Suits)": False,
        "Deceptive-Fives (6 Suits)": False,
        "Funnels (6 Suits)": True,
        "Chimneys (6 Suits)": True,
        "Ambiguous (6 Suits)": False,
        "Very Ambiguous (6 Suits)": False,
        "Extremely Ambiguous (6 Suits)": False,
        "Holiday Mix (5 Suits)": True,
        "Holiday Mix (6 Suits)": True,
    }
    run_simple_test(game_state.is_brownish_pinkish, tests)


def test_is_whiteish_rainbowy():
    tests = {
        "No Variant": False,
        "Black (5 Suits)": False,
        "Prism (5 Suits)": False,
        "Dark Prism (5 Suits)": False,
        "Black & Dark Prism (6 Suits)": False,
        "Rainbow (5 Suits)": True,
        "Dark Rainbow (5 Suits)": True,
        "White (5 Suits)": True,
        "Gray (5 Suits)": True,
        "Brown (6 Suits)": False,
        "Dark Brown (6 Suits)": False,
        "Gray & Dark Brown (6 Suits)": True,
        "Pink (6 Suits)": False,
        "Dark Pink (6 Suits)": False,
        "Light Pink (6 Suits)": True,
        "Gray Pink (6 Suits)": True,
        "Muddy Rainbow (6 Suits)": True,
        "Cocoa Rainbow (6 Suits)": True,
        "Omni (6 Suits)": True,
        "Dark Omni (6 Suits)": True,
        "Null (6 Suits)": True,
        "Dark Null (6 Suits)": True,
        "Special Mix (5 Suits)": True,
        "Special Mix (6 Suits)": True,
        "Valentine Mix (5 Suits)": True,
        "Valentine Mix (6 Suits)": True,
        "White-Ones (6 Suits)": True,
        "Rainbow-Ones (6 Suits)": True,
        "Pink-Ones (6 Suits)": False,
        "Brown-Ones (6 Suits)": False,
        "Null-Ones (6 Suits)": True,
        "Deceptive-Ones (6 Suits)": False,
        "Deceptive-Fives (6 Suits)": False,
        "Funnels (6 Suits)": False,
        "Chimneys (6 Suits)": False,
        "Ambiguous (6 Suits)": False,
        "Very Ambiguous (6 Suits)": False,
        "Extremely Ambiguous (6 Suits)": False,
        "Holiday Mix (5 Suits)": True,
        "Holiday Mix (6 Suits)": True,
    }
    run_simple_test(game_state.is_whiteish_rainbowy, tests)


def test_all():
    t0 = dt.datetime.now()
    test_get_available_rank_clues()
    test_get_available_color_clues()
    test_get_all_touched_cards()
    test_is_brownish_pinkish()
    test_is_whiteish_rainbowy()
    t1 = dt.datetime.now()
    print(f"All tests passed in {(t1 - t0).total_seconds():.2f}s!")


if __name__ == "__main__":
    test_all()
