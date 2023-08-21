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
        act = fn(input) if isinstance(input, str) else fn(*input)
        fn_name = fn.__name__
        assert act == exp, f"{fn_name}\nInput: {input}\nExpected: {exp}\nActual: {act}"
    print(f"{len(tests)} tests for {fn_name} passed!")


def test_get_num_available_color_clues():
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
    }
    run_simple_test(game_state.is_whiteish_rainbowy, tests)


def test_all():
    t0 = dt.datetime.now()
    test_get_num_available_color_clues()
    test_get_all_touched_cards()
    test_is_brownish_pinkish()
    test_is_whiteish_rainbowy()
    t1 = dt.datetime.now()
    print(f"All tests passed in {(t1 - t0).total_seconds():.2f}s!")


if __name__ == "__main__":
    test_all()
