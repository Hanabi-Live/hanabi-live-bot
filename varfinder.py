from html.parser import HTMLParser
import requests
from game_state import SUITS, DARK_SUIT_NAMES


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.data = []

    def handle_starttag(self, tag, attrs):
        return

    def handle_data(self, data):
        if data in SUITS:
            self.data.append(data)

    def handle_endtag(self, tag):
        return


def get_missing_vars(
    username,
    num_players,
    include_dark_suits=True,
    num_suits=None,
    include_substrings=None,
    exclude_substrings=None,
    shorthand=True,
):
    url = f"https://hanab.live/missing-scores/{username}/{num_players}"
    parser = Parser()
    parser.feed(requests.get(url).text)

    vars = set(parser.data)
    if not include_dark_suits:
        to_remove = set()
        for x in vars:
            for dark_suit in DARK_SUIT_NAMES:
                if dark_suit in x:
                    to_remove.add(x)
        vars = vars.difference(to_remove)

    if num_suits is not None:
        vars = {x for x in vars if f"{num_suits} Suits" in x}

    if include_substrings is not None:
        to_keep = set()
        for x in vars:
            for substr in include_substrings:
                if substr in x:
                    to_keep.add(x)
        vars = vars.intersection(to_keep)

    if exclude_substrings is not None:
        to_remove = set()
        for x in vars:
            for substr in exclude_substrings:
                if substr in x:
                    to_remove.add(x)
        vars = vars.difference(to_remove)

    if shorthand:
        return [
            x.replace(" & ", "+")
            .replace(" (", "_")
            .replace(" Suits)", "s")
            .replace(" ", "_")
            for x in vars
        ]
    return list(vars)


if __name__ == "__main__":
    exclude_substrings = [
        "Throw",
        "Matryoshka",
        "Dual-Color",
        "Ambig",
        "Reversed",
        "Up or Down",
        "Alternating",
        "Duck",
        "Cow",
        "Odds and Evens",
        "Synesthesia",
        "-Ones",
        "-Fives",
        "Clue Starved",
        "Funnels",
        "Chimneys",
    ]
    include_substrings = None

    exclude_substrings = None
    include_substrings = ["Omni-Ones"]
    vars = get_missing_vars(
        "yagami_black",
        5,
        include_dark_suits=True,
        num_suits=6,
        include_substrings=include_substrings,
        exclude_substrings=exclude_substrings,
        shorthand=True,
    )
    print(vars)
    print(len(vars))
