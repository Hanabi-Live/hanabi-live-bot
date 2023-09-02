from constants import MAX_CLUE_NUM, COLOR_CLUE, RANK_CLUE

import os
import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import numpy as np
import itertools

variants_file = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), "variants.json"
)
with open(variants_file, "r") as f:
    VARIANT_INFO = json.load(f)

SUITS = {x["name"]: x["suits"] for x in VARIANT_INFO}
DARK_SUIT_NAMES = {
    "Black",
    "Gray",
    "Dark Rainbow",
    "Dark Prism",
    "Dark Pink",
    "Dark Brown",
    "Dark Omni",
    "Gray Pink",
    "Cocoa Rainbow",
    "Dark Null",
}


@dataclass
class Card:
    order: int
    suit_index: int
    rank: int

    def __eq__(self, other):
        return (self.suit_index == other.suit_index) and (self.rank == other.rank)

    def __str__(self):
        if self.suit_index == -1:
            return "Unknown"
        return str(self.to_tuple())

    def __repr__(self):
        return self.__str__()

    def to_tuple(self) -> Tuple[int, int]:
        return (self.suit_index, self.rank)


def get_available_rank_clues(variant_name: str):
    for substr in [
        "Pink-Ones",
        "Light-Pink-Ones",
        "Omni-Ones",
        "Brown-Ones",
        "Muddy-Rainbow-Ones",
        "Null-Ones",
        "Deceptive-Ones",
    ]:
        if substr in variant_name:
            return [2, 3, 4, 5]

    for substr in [
        "Pink-Fives",
        "Light-Pink-Fives",
        "Omni-Fives",
        "Brown-Fives",
        "Muddy-Rainbow-Fives",
        "Null-Fives",
        "Deceptive-Fives",
    ]:
        if substr in variant_name:
            return [1, 2, 3, 4]

    if "Odds and Evens" in variant_name:
        return [1, 2]

    return [1, 2, 3, 4, 5]


def get_available_color_clues(variant_name: str):
    # TODO - handle nonstandard suits like ambiguous, dual color, etc.
    available_color_clues = []
    for color in [
        "Red",
        "Yellow",
        "Green",
        "Blue",
        "Purple",
        "Teal",
        "Black",
        "Pink",
        "Dark Pink",
        "Brown",
        "Dark Brown",
    ]:
        if color in SUITS[variant_name]:
            available_color_clues.append(color)

    return available_color_clues


def get_all_cards(variant_name: str) -> Set[Tuple[int, int]]:
    cards = set()
    for i, suit in enumerate(SUITS[variant_name]):
        for rank in range(1, 6):
            cards.add((i, rank))

    return cards


def get_all_cards_with_multiplicity(variant_name: str) -> List[Tuple[int, int]]:
    cards = []
    for i, suit in enumerate(SUITS[variant_name]):
        for rank in range(1, 6):
            cards.append((i, rank))
            if suit not in DARK_SUIT_NAMES and rank == 1:
                cards.append((i, rank))
                cards.append((i, rank))
            elif suit not in DARK_SUIT_NAMES and rank in {2, 3, 4}:
                cards.append((i, rank))

    return cards


def get_all_touched_cards(
    clue_type: int, clue_value: int, variant_name: str
) -> Set[Tuple[int, int]]:
    # TODO - handle nonstandard suits like ambiguous, dual color, etc.
    # TODO - handle special 1s and 5s
    available_color_clues = get_available_color_clues(variant_name)
    prism_touch = list(zip(available_color_clues * 5, [1, 2, 3, 4, 5]))
    cards = set()
    for i, suit in enumerate(SUITS[variant_name]):
        for rank in range(1, 6):
            if clue_type == COLOR_CLUE:
                if suit in {
                    "Rainbow",
                    "Dark Rainbow",
                    "Muddy Rainbow",
                    "Cocoa Rainbow",
                    "Omni",
                    "Dark Omni",
                }:
                    cards.add((i, rank))

                if suit in available_color_clues[clue_value]:
                    if (
                        "White-Ones" in variant_name
                        or "Light-Pink-Ones" in variant_name
                        or "Null-Ones" in variant_name
                    ) and rank == 1:
                        continue
                    elif (
                        "White-Fives" in variant_name
                        or "Light-Pink-Fives" in variant_name
                        or "Null-Fives" in variant_name
                    ) and rank == 5:
                        continue
                    else:
                        cards.add((i, rank))

                if (
                    suit in {"Prism", "Dark Prism"}
                    and (available_color_clues[clue_value], rank) in prism_touch
                ):
                    cards.add((i, rank))

                if (
                    (
                        "Rainbow-Ones" in variant_name
                        or "Muddy-Rainbow-Ones" in variant_name
                        or "Omni-Ones" in variant_name
                    )
                    and rank == 1
                    and suit
                    not in {
                        "White",
                        "Light Pink",
                        "Null",
                        "Gray",
                        "Gray Pink",
                        "Dark Null",
                    }
                ):
                    cards.add((i, rank))

                if (
                    (
                        "Rainbow-Fives" in variant_name
                        or "Muddy-Rainbow-Fives" in variant_name
                        or "Omni-Fives" in variant_name
                    )
                    and rank == 5
                    and suit
                    not in {
                        "White",
                        "Light Pink",
                        "Null",
                        "Gray",
                        "Gray Pink",
                        "Dark Null",
                    }
                ):
                    cards.add((i, rank))

            elif clue_type == RANK_CLUE:
                if suit in {
                    "Pink",
                    "Dark Pink",
                    "Light Pink",
                    "Gray Pink",
                    "Omni",
                    "Dark Omni",
                }:
                    cards.add((i, rank))
                if suit not in {
                    "Brown",
                    "Dark Brown",
                    "Muddy Rainbow",
                    "Cocoa Rainbow",
                    "Null",
                    "Dark Null",
                }:
                    if (clue_value == rank) and ("Odds and Evens" not in variant_name):
                        cards.add((i, rank))
                    elif (clue_value == rank % 2) and (
                        "Odds and Evens" in variant_name
                    ):
                        cards.add((i, rank))
                if (
                    (
                        "Pink-Ones" in variant_name
                        or "Light-Pink-Ones" in variant_name
                        or "Omni-Ones" in variant_name
                    )
                    and rank == 1
                    and suit
                    not in {
                        "Brown",
                        "Muddy Rainbow",
                        "Null",
                        "Dark Brown",
                        "Cocoa Rainbow",
                        "Dark Null",
                    }
                ):
                    cards.add((i, rank))
                if (
                    (
                        "Pink-Fives" in variant_name
                        or "Light-Pink-Fives" in variant_name
                        or "Omni-Fives" in variant_name
                    )
                    and rank == 5
                    and suit
                    not in {
                        "Brown",
                        "Muddy Rainbow",
                        "Null",
                        "Dark Brown",
                        "Cocoa Rainbow",
                        "Dark Null",
                    }
                ):
                    cards.add((i, rank))
    return cards


def get_all_non_touched_cards(clue_type: int, clue_value: int, variant_name: str):
    all_cards = get_all_cards(variant_name)
    return all_cards.difference(
        get_all_touched_cards(clue_type, clue_value, variant_name)
    )


def is_brownish_pinkish(variant_name):
    num_suits = len(SUITS[variant_name])
    for rank in range(1, 6):
        cards_touched = get_all_touched_cards(RANK_CLUE, rank, variant_name)
        if len(cards_touched) != num_suits:
            return True
    return False


def is_whiteish_rainbowy(variant_name):
    available_color_clues = get_available_color_clues(variant_name)
    num_colors_touching_card = {x: 0 for x in get_all_cards(variant_name)}
    for color in range(len(available_color_clues)):
        cards_touched = get_all_touched_cards(COLOR_CLUE, color, variant_name)
        for x in cards_touched:
            num_colors_touching_card[x] += 1

    for i, num_colors in num_colors_touching_card.items():
        if num_colors != 1:
            return True
    return False


def get_candidates_list_str(
    candidates_list: List[Tuple[int, int]],
    variant_name: str,
    actual_hand=None,
    poss_list=None,
):
    output = ""

    for rank in range(1, 6):
        output += "\n"
        for hand_order, candidates in enumerate(candidates_list):
            output += "  "
            for i, suit in enumerate(SUITS[variant_name]):
                if (i, rank) in candidates:
                    _char = "*"
                    if actual_hand is not None:
                        actual_card = actual_hand[hand_order]
                        if (i == actual_card.suit_index) and (rank == actual_card.rank):
                            _char = "O"
                    output += _char
                elif poss_list is not None and (i, rank) in poss_list[hand_order]:
                    output += "x"
                else:
                    output += "."

    return output


def get_starting_pace(num_players: int, variant_name: str):
    num_suits = len(SUITS[variant_name])
    base_starting_pace = {6: 18, 5: 15, 4: 18, 3: 18, 2: 22}[num_players]
    num_dark_suits = len({x for x in SUITS[variant_name] if x in DARK_SUIT_NAMES})
    return base_starting_pace - (6 - num_suits) * 5 - num_dark_suits * 5


class GameState:
    def __init__(self, variant_name, player_names, our_player_index):
        self.set_variant_name(variant_name, len(player_names))
        self.player_names: List[str] = player_names
        self.our_player_index: int = our_player_index
        self.current_player_index: int = 0

        # Initialize the hands for each player (an array of cards)
        self.hands: Dict[int, List[Card]] = {}

        # possibilities include only positive/negative information
        # candidates further narrow possibilities based on conventions
        self.all_possibilities_list: Dict[int, List[Set[Tuple[int, int]]]] = {}
        self.all_candidates_list: Dict[int, List[Set[Tuple[int, int]]]] = {}
        for i in range(len(player_names)):
            self.hands[i] = []
            self.all_possibilities_list[i] = []
            self.all_candidates_list[i] = []

        self.clue_tokens: int = MAX_CLUE_NUM
        self.bombs: int = 0
        self.rank_clued_card_orders: Dict[int, List[int]] = {}  # order -> clue vals
        self.color_clued_card_orders: Dict[int, List[int]] = {}  # order -> clue vals
        self.other_info_clued_card_orders: Dict[str, Set[int]] = {}
        self.stacks: List[int] = [0] * len(SUITS[variant_name])
        self.discards: Dict[
            Tuple[int, int], int
        ] = {}  # keys are tuples of (suit_index, rank)
        self.turn: int = 0
        self.notes: Dict[int, str] = {}

    @property
    def num_players(self) -> int:
        return len(self.player_names)

    @property
    def our_player_name(self) -> str:
        return self.player_names[self.our_player_index]

    @property
    def playables(self) -> Set[Tuple[int, int]]:
        # TODO: handle reversed
        return set([(suit, stack + 1) for suit, stack in enumerate(self.stacks)])

    @property
    def score_pct(self) -> float:
        return sum(self.stacks) / (5 * len(self.stacks))

    @property
    def max_num_cards(self) -> Dict[Tuple[int, int], int]:
        all_cards = get_all_cards(self.variant_name)
        result = {}
        for suit_index, rank in all_cards:
            result[(suit_index, rank)] = 1
            if SUITS[self.variant_name][suit_index] not in DARK_SUIT_NAMES:
                if rank in {2, 3, 4}:
                    result[(suit_index, rank)] += 1
                elif rank == 1:
                    result[(suit_index, rank)] += 2
        return result

    @property
    def criticals(self) -> Set[Tuple[int, int]]:
        # TODO: handle reversed
        trash = self.trash
        crits = set()
        for (suit, rank), max_num in self.max_num_cards.items():
            if (suit, rank) in trash:
                continue
            if self.discards.get((suit, rank), 0) == max_num - 1:
                crits.add((suit, rank))
        return crits

    @property
    def non_5_criticals(self) -> Set[Tuple[int, int]]:
        return {(suit, rank) for (suit, rank) in self.criticals if rank != 5}

    @property
    def trash(self) -> Set[Tuple[int, int]]:
        # TODO: handle reversed
        trash_cards = set()
        for suit, stack in enumerate(self.stacks):
            for i in range(stack):
                trash_cards.add((suit, i + 1))

        dead_suits = {suit: 5 for suit, _ in enumerate(self.stacks)}
        max_num_cards = self.max_num_cards
        for (suit, rank), num_discards in self.discards.items():
            assert num_discards <= max_num_cards[(suit, rank)]
            if num_discards == max_num_cards[(suit, rank)]:
                dead_suits[suit] = min(rank, dead_suits[suit])

        for suit, dead_from in dead_suits.items():
            for i in range(dead_from + 1, 6):
                trash_cards.add((suit, i))
        return trash_cards

    @property
    def pace(self) -> int:
        return get_starting_pace(self.num_players, self.variant_name) - sum(
            self.discards.values()
        )

    @property
    def num_cards_in_deck(self) -> int:
        total_cards = len(get_all_cards_with_multiplicity(self.variant_name))
        cards_dealt = {2: 10, 3: 15, 4: 16, 5: 20, 6: 18}[self.num_players]
        return max(
            0,
            total_cards - cards_dealt - sum(self.discards.values()) - sum(self.stacks),
        )

    @property
    def our_hand(self) -> List[Card]:
        return self.hands[self.our_player_index]

    @property
    def our_candidates(self) -> List[Set[Tuple[int, int]]]:
        return self.all_candidates_list[self.our_player_index]

    @property
    def our_possibilities(self) -> List[Set[Tuple[int, int]]]:
        return self.all_possibilities_list[self.our_player_index]

    @property
    def num_1s_played(self) -> int:
        return sum([x > 0 for x in self.stacks])

    @property
    def order_to_index(self) -> Dict[int, Tuple[int, int]]:
        result = {}
        for player_index, hand in self.hands.items():
            for i, card in enumerate(hand):
                result[card.order] = (player_index, i)
        return result

    def get_candidates(self, order) -> Set[Tuple[int, int]]:
        player_index, i = self.order_to_index[order]
        return self.all_candidates_list[player_index][i]

    def get_possibilities(self, order) -> Set[Tuple[int, int]]:
        player_index, i = self.order_to_index[order]
        return self.all_possibilities_list[player_index][i]

    def get_card(self, order) -> Card:
        player_index, i = self.order_to_index[order]
        return self.hands[player_index][i]

    def is_playable(self, candidates: Set[Tuple[int, int]]) -> bool:
        return not len(candidates.difference(self.playables)) and len(candidates)

    def is_playable_card(self, card: Card) -> bool:
        return (card.suit_index, card.rank) in self.playables

    def is_trash(self, candidates: Set[Tuple[int, int]]) -> bool:
        return not len(candidates.difference(self.trash)) and len(candidates)

    def is_trash_card(self, card: Card) -> bool:
        return (card.suit_index, card.rank) in self.trash

    def is_critical(self, candidates: Set[Tuple[int, int]]) -> bool:
        return not len(candidates.difference(self.criticals)) and len(candidates)

    def is_critical_card(self, card: Card) -> bool:
        return (card.suit_index, card.rank) in self.criticals

    def is_clued(self, order) -> bool:
        return (
            order in self.color_clued_card_orders
            or order in self.rank_clued_card_orders
        )

    def get_clued_orders(self, player_index: int) -> List[int]:
        # returns orders from right to left
        return [
            x.order
            for x in self.hands[player_index]
            if x.order in self.color_clued_card_orders
            or x.order in self.rank_clued_card_orders
        ]

    def get_unclued_orders(self, player_index: int) -> List[int]:
        # returns orders from right to left
        return [
            x.order
            for x in self.hands[player_index]
            if x.order not in self.color_clued_card_orders
            and x.order not in self.rank_clued_card_orders
        ]

    def get_all_other_players_cards(self, player_index=None) -> Set[Tuple[int, int]]:
        return {
            (c.suit_index, c.rank)
            for pindex, hand in self.hands.items()
            for c in hand
            if pindex not in {self.our_player_index, player_index}
        }

    def get_all_other_players_clued_cards(
        self, player_index=None
    ) -> Set[Tuple[int, int]]:
        return {
            (c.suit_index, c.rank)
            for pindex, hand in self.hands.items()
            for c in hand
            if pindex not in {self.our_player_index, player_index}
            and (
                c.order in self.color_clued_card_orders
                or c.order in self.rank_clued_card_orders
            )
        }

    def set_variant_name(self, variant_name: str, num_players: int):
        self.variant_name = variant_name
        self.stacks = [0] * len(SUITS[self.variant_name])

    def get_copies_visible(self, player_index, suit, rank) -> int:
        num = self.discards.get((suit, rank), 0)
        if self.stacks[suit] >= rank:
            num += 1

        for i in range(self.num_players):
            if i == player_index:
                continue
            for card in self.hands[i]:
                if (card.suit_index, card.rank) == (suit, rank):
                    num += 1
        return num

    def get_fully_known_card_orders(
        self, player_index: int, query_candidates=True, keyed_on_order=False
    ) -> Dict[Tuple[int, int], List[int]]:
        poss_list = (
            self.all_candidates_list[player_index]
            if query_candidates
            else self.all_possibilities_list[player_index]
        )
        orders = {}
        for i, poss in enumerate(poss_list):
            if len(poss) == 1:
                singleton = list(poss)[0]
                if keyed_on_order:
                    orders[self.hands[player_index][i].order] = singleton
                else:
                    if singleton not in orders:
                        orders[singleton] = []
                    orders[singleton].append(self.hands[player_index][i].order)
        return orders

    def get_doubleton_orders(self, player_index: int, query_candidates=True):
        poss_list = (
            self.all_candidates_list[player_index]
            if query_candidates
            else self.all_possibilities_list[player_index]
        )
        orders = {}
        for i, poss in enumerate(poss_list):
            if len(poss) == 2:
                doubleton_tup = tuple(sorted([list(poss)[0], list(poss)[1]]))
                if doubleton_tup not in orders:
                    orders[doubleton_tup] = []
                orders[doubleton_tup].append(self.hands[player_index][i].order)
        return orders

    def get_tripleton_orders(self, player_index: int, query_candidates=True):
        poss_list = (
            self.all_candidates_list[player_index]
            if query_candidates
            else self.all_possibilities_list[player_index]
        )
        orders = {}
        possible_tripleton_candidates = set()
        for i, poss in enumerate(poss_list):
            if len(poss) in {2, 3}:
                for candidate in poss:
                    possible_tripleton_candidates.add(candidate)

        for tripleton in itertools.combinations(possible_tripleton_candidates, 3):
            orders[tripleton] = []
            for i, poss in enumerate(poss_list):
                if not len(poss.difference(set(tripleton))):
                    orders[tripleton].append(self.hands[player_index][i].order)
        return orders

    def _process_visible_cards(self, query_candidates=True):
        max_num_cards = self.max_num_cards
        for player_index in range(self.num_players):
            poss_list = (
                self.all_candidates_list[player_index]
                if query_candidates
                else self.all_possibilities_list[player_index]
            )
            fk_orders = self.get_fully_known_card_orders(player_index, query_candidates)
            for i, poss in enumerate(poss_list):
                this_order = self.hands[player_index][i].order
                removed_cards = set()
                for suit, rank in poss:
                    copies_visible = self.get_copies_visible(player_index, suit, rank)
                    # copies visible is only for other players' hands and discard pile
                    # also incorporate information from my own hand
                    for (fk_si, fk_rank), orders in fk_orders.items():
                        for order in orders:
                            if order != this_order and (fk_si, fk_rank) == (suit, rank):
                                copies_visible += 1

                    if max_num_cards[(suit, rank)] == copies_visible:
                        removed_cards.add((suit, rank))

                poss_list[i] = poss_list[i].difference(removed_cards)

    def _process_doubletons(self, query_candidates=True):
        maxcds = self.max_num_cards
        for player_index in range(self.num_players):
            poss_list = (
                self.all_candidates_list[player_index]
                if query_candidates
                else self.all_possibilities_list[player_index]
            )
            doubleton_orders = self.get_doubleton_orders(player_index, query_candidates)
            for doubleton, orders in doubleton_orders.items():
                if len(orders) < 2:
                    continue

                first, second = doubleton
                s1_vis = self.get_copies_visible(player_index, first[0], first[1])
                s2_vis = self.get_copies_visible(player_index, second[0], second[1])
                if len(orders) < maxcds[first] + maxcds[second] - s1_vis - s2_vis:
                    continue

                for i, _ in enumerate(poss_list):
                    if self.hands[player_index][i].order not in orders:
                        poss_list[i] = poss_list[i].difference({first, second})

    def _process_tripletons(self, query_candidates=True):
        maxcds = self.max_num_cards
        for player_index in range(self.num_players):
            poss_list = (
                self.all_candidates_list[player_index]
                if query_candidates
                else self.all_possibilities_list[player_index]
            )
            tripleton_orders = self.get_tripleton_orders(player_index, query_candidates)
            for tripleton, orders in tripleton_orders.items():
                if len(orders) < 3:
                    continue

                first, second, third = tripleton
                s1_vis = self.get_copies_visible(player_index, first[0], first[1])
                s2_vis = self.get_copies_visible(player_index, second[0], second[1])
                s3_vis = self.get_copies_visible(player_index, third[0], third[1])
                _1sts, _2nds, _3rds = maxcds[first], maxcds[second], maxcds[third]
                if len(orders) < _1sts + _2nds + _3rds - s1_vis - s2_vis - s3_vis:
                    continue

                for i, _ in enumerate(poss_list):
                    if self.hands[player_index][i].order not in orders:
                        poss_list[i] = poss_list[i].difference({first, second, third})

    def process_visible_cards(self):
        for _ in range(3):
            self._process_visible_cards(True)
            self._process_doubletons(True)
            self._process_tripletons(True)
            self._process_visible_cards(False)
            self._process_doubletons(False)
            self._process_tripletons(False)

    def print(self):
        our_player_name = self.player_names[self.our_player_index]
        current_player = self.player_names[self.current_player_index]
        output = f"\nVariant: {self.variant_name}, POV: {our_player_name}\n"
        output += f"Turn: {self.turn + 1}, currently on {current_player}\n"
        output += (
            f"Clues: {self.clue_tokens}, Bombs: {self.bombs}, "
            f"Pace: {self.pace}, Cards: {self.num_cards_in_deck}\n"
        )
        output += (
            "Stacks: "
            + ", ".join(
                [
                    suit_name + " " + str(self.stacks[i])
                    for i, suit_name in enumerate(SUITS[self.variant_name])
                ]
            )
            + "\n"
        )

        output += "\n"
        for i, name in enumerate(self.player_names):
            candidates_list = self.all_candidates_list[i]
            poss_list = self.all_possibilities_list[i]
            output += (
                name
                + "\nOrders: "
                + ", ".join([str(card.order) for card in reversed(self.hands[i])])
            )
            output += "\nNotes: " + ", ".join(
                [
                    "'" + self.notes.get(card.order, "") + "'"
                    for card in reversed(self.hands[i])
                ]
            )
            output += get_candidates_list_str(
                list(reversed(candidates_list)),
                self.variant_name,
                list(reversed(self.hands[i])),
                list(reversed(poss_list)),
            )
            output += "\n  "
            for card in reversed(self.hands[i]):
                if (
                    card.order in self.rank_clued_card_orders
                    and card.order in self.color_clued_card_orders
                ):
                    output += "+"
                elif card.order in self.rank_clued_card_orders:
                    output += "-"
                elif card.order in self.color_clued_card_orders:
                    output += "|"
                else:
                    output += " "

                for _id, orders in self.other_info_clued_card_orders.items():
                    output += _id[0].upper() if card.order in orders else " "
                output += " " * (
                    len(SUITS[self.variant_name])
                    + 1
                    - len(self.other_info_clued_card_orders)
                )
            output += "\n"

        output += "Discards:\n"
        for rank in range(1, 6):
            output += "  "
            for suit_index, suit in enumerate(SUITS[self.variant_name]):
                num_discards = self.discards.get((suit_index, rank), 0)
                output += str(num_discards) if num_discards > 0 else "."
            output += "\n"

        print(output)

    def remove_card_from_hand(self, player_index, order):
        hand = self.hands[player_index]
        card_index = None
        for i in range(len(hand)):
            card = hand[i]
            if card.order == order:
                card_index = i

        assert card_index is not None, f"can't find #{order} in {player_index}'s hand"
        card = hand[card_index]
        del hand[card_index]
        del self.all_candidates_list[player_index][card_index]
        del self.all_possibilities_list[player_index][card_index]
        return card

    def handle_draw(self, player_index, order, suit_index, rank):
        new_card = Card(order=order, suit_index=suit_index, rank=rank)
        self.hands[player_index].append(new_card)
        self.all_candidates_list[player_index].append(get_all_cards(self.variant_name))
        self.all_possibilities_list[player_index].append(
            get_all_cards(self.variant_name)
        )
        self.process_visible_cards()
        return new_card

    def handle_play(self, player_index, order, suit_index, rank):
        self.remove_card_from_hand(player_index, order)
        self.stacks[suit_index] = rank
        self.process_visible_cards()
        return Card(order, suit_index, rank)

    def handle_discard(self, player_index, order, suit_index, rank):
        self.remove_card_from_hand(player_index, order)
        if (suit_index, rank) not in self.discards:
            self.discards[(suit_index, rank)] = 1
        else:
            self.discards[(suit_index, rank)] += 1
        self.process_visible_cards()
        return Card(order, suit_index, rank)

    def super_handle_clue(
        self,
        clue_giver: int,
        target_index: int,
        clue_type: int,
        clue_value: int,
        card_orders,
    ):
        return self.handle_clue(
            clue_giver, target_index, clue_type, clue_value, card_orders
        )

    def handle_clue(
        self,
        clue_giver: int,
        target_index: int,
        clue_type: int,
        clue_value: int,
        card_orders,
    ):
        all_cards_touched_by_clue = get_all_touched_cards(
            clue_type, clue_value, self.variant_name
        )
        touched_cards = []
        candidates_list = self.all_candidates_list[target_index]
        poss_list = self.all_possibilities_list[target_index]

        for i, card in enumerate(self.hands[target_index]):
            if card.order in card_orders:
                touched_cards.append(card)
                new_candidates = candidates_list[i].intersection(
                    all_cards_touched_by_clue
                )
                new_possibilities = poss_list[i].intersection(all_cards_touched_by_clue)
                poss_list[i] = new_possibilities
                if not len(new_candidates):
                    self.write_note(card.order, note="Positive clue conflict!")
                    candidates_list[i] = new_possibilities
                else:
                    candidates_list[i] = new_candidates
            else:
                new_candidates = candidates_list[i].difference(
                    all_cards_touched_by_clue
                )
                new_possibilities = poss_list[i].difference(all_cards_touched_by_clue)
                poss_list[i] = new_possibilities
                if not len(new_candidates):
                    self.write_note(card.order, note="Negative clue conflict!")
                    candidates_list[i] = new_possibilities
                else:
                    candidates_list[i] = new_candidates

        for order in card_orders:
            if clue_type == RANK_CLUE:
                if order not in self.rank_clued_card_orders:
                    self.rank_clued_card_orders[order] = []
                self.rank_clued_card_orders[order].append(clue_value)
            elif clue_type == COLOR_CLUE:
                if order not in self.color_clued_card_orders:
                    self.color_clued_card_orders[order] = []
                self.color_clued_card_orders[order].append(clue_value)

        return touched_cards

    def get_cards_touched_dict(
        self, target_index: int, clue_type_values: Tuple[int, int]
    ) -> Dict[Tuple[int, int, int], Set[Tuple[int, int]]]:
        target_hand = self.hands[target_index]
        clue_to_cards_touched = {}
        available_color_clues = get_available_color_clues(self.variant_name)
        available_rank_clues = get_available_rank_clues(self.variant_name)
        for clue_type, clue_value in clue_type_values:
            # prevent illegal clues from being given
            if clue_type == COLOR_CLUE and clue_value >= len(available_color_clues):
                continue
            if clue_type == RANK_CLUE and clue_value not in available_rank_clues:
                continue

            cards_touched = get_all_touched_cards(
                clue_type, clue_value, self.variant_name
            )
            cards_touched_in_target_hand = [
                card
                for card in target_hand
                if (card.suit_index, card.rank) in cards_touched
            ]
            if len(cards_touched_in_target_hand):
                clue_to_cards_touched[
                    (clue_type, clue_value)
                ] = cards_touched_in_target_hand
        return {
            (clue_value, clue_type, target_index): cards_touched
            for (clue_type, clue_value), cards_touched in clue_to_cards_touched.items()
        }

    def get_good_actions(self, player_index: int) -> Dict[str, List[int]]:
        raise NotImplementedError

    def get_legal_clues(self) -> Dict[Tuple[int, int, int], Set[Tuple[int, int]]]:
        # (clue_value, clue_type, target_index) -> cards_touched
        raise NotImplementedError

    def write_note(self, order: int, note: str, candidates=None, append=True):
        _note = "t" + str(self.turn + 1) + ": "
        if candidates is not None:
            suit_names = SUITS[self.variant_name]
            if not self.is_trash(candidates):
                _note += (
                    "["
                    + ",".join(
                        [
                            suit_names[suit_index] + " " + str(rank)
                            for (suit_index, rank) in candidates
                        ]
                    )
                    + "]"
                )
            else:
                _note += "[trash]"
        _note += note

        if order not in self.notes:
            self.notes[order] = _note
            return

        if append:
            self.notes[order] += " | " + _note
        else:
            self.notes[order] = _note
