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
        return str((self.suit_index, self.rank))

    def __repr__(self):
        return self.__str__()


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


def get_all_cards(variant_name: str):
    cards = set()
    for i, suit in enumerate(SUITS[variant_name]):
        for rank in range(1, 6):
            cards.add((i, rank))

    return cards


def get_all_cards_with_multiplicity(variant_name: str):
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


def get_random_deck(variant_name: str):
    # usually used for testing purposes
    cards = get_all_cards_with_multiplicity(variant_name)
    perm = np.random.permutation(cards)
    return [Card(order, x[0], x[1]) for order, x in enumerate(perm)]


def get_all_touched_cards(clue_type: int, clue_value: int, variant_name: str):
    # TODO - handle nonstandard suits like ambiguous, dual color, etc.
    # TODO - handle special 1s and 5s
    available_color_clues = get_available_color_clues(variant_name)
    prism_touch = list(zip(available_color_clues * 5, [1, 2, 3, 4, 5]))

    cards = set()
    for i, suit in enumerate(SUITS[variant_name]):
        for rank in range(1, 6):
            if clue_type == COLOR_CLUE:
                if suit in {
                    available_color_clues[clue_value],
                    "Rainbow",
                    "Dark Rainbow",
                    "Muddy Rainbow",
                    "Cocoa Rainbow",
                    "Omni",
                    "Dark Omni",
                }:
                    cards.add((i, rank))
                if (
                    suit in {"Prism", "Dark Prism"}
                    and (available_color_clues[clue_value], rank) in prism_touch
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
                if (
                    suit
                    not in {
                        "Brown",
                        "Dark Brown",
                        "Muddy Rainbow",
                        "Cocoa Rainbow",
                        "Null",
                        "Dark Null",
                    }
                    and clue_value == rank
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


def get_candidates_list_str(candidates_list, variant_name: str, actual_hand=None):
    output = ""

    for rank in range(1, 6):
        output += "\n"
        for hand_order, candidates in enumerate(candidates_list):
            output += "  "
            for i, suit in enumerate(SUITS[variant_name]):
                if (i, rank) in candidates:
                    if actual_hand is not None:
                        actual_card = actual_hand[hand_order]
                        output += (
                            "x"
                            if (i == actual_card.suit_index)
                            and (rank == actual_card.rank)
                            else "*"
                        )
                    else:
                        output += "*"
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
        self.all_candidates_list: Dict[int, List[Set[Tuple[int, int]]]] = {}
        for i in range(len(player_names)):
            self.hands[i] = []
            self.all_candidates_list[i] = []

        self.clue_tokens: int = MAX_CLUE_NUM
        self.bombs: int = 0
        self.rank_clued_card_orders: Dict[int, List[int]] = {}    # order -> clue vals
        self.color_clued_card_orders: Dict[int, List[int]] = {}    # order -> clue vals
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
    def criticals(self) -> Set[Tuple[int, int]]:
        # TODO: handle reversed
        fives = set([(suit, 5) for suit in range(len(self.stacks))])
        dark_suits = set(
            [
                (suit, i)
                for i in range(1, 6)
                for suit, suit_name in enumerate(SUITS[self.variant_name])
                if suit_name in DARK_SUIT_NAMES
            ]
        )
        all_trash = self.trash
        other_crits = set()
        for (suit, rank), num_discards in self.discards.items():
            if (suit, rank) in all_trash:
                continue
            if rank == 1 and num_discards == 2:
                other_crits.add((suit, rank))
            if rank in {2, 3, 4} and num_discards == 1:
                other_crits.add((suit, rank))
        return fives.union(dark_suits).union(other_crits)

    @property
    def trash(self) -> Set[Tuple[int, int]]:
        # TODO: handle reversed
        # TODO: maybe handle the case where if all copies of a card were discarded then the rest is trash
        trash_cards = set()
        for suit, stack in enumerate(self.stacks):
            for i in range(stack):
                trash_cards.add((suit, i + 1))
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
        return (
            total_cards - cards_dealt - sum(self.discards.values()) - sum(self.stacks)
        )

    @property
    def our_hand(self) -> List[Card]:
        return self.hands[self.our_player_index]

    @property
    def our_candidates(self) -> List[Set[Tuple[int, int]]]:
        return self.all_candidates_list[self.our_player_index]

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

    def get_card(self, order) -> Card:
        player_index, i = self.order_to_index[order]
        return self.hands[player_index][i]

    def is_playable(self, candidates) -> bool:
        return not len(candidates.difference(self.playables))

    def is_trash(self, candidates) -> bool:
        return not len(candidates.difference(self.trash))

    def is_critical(self, candidates) -> bool:
        return not len(candidates.difference(self.criticals))

    def get_all_other_players_cards(self, player_index=None) -> Set[Tuple[int, int]]:
        return {
            (c.suit_index, c.rank)
            for pindex, hand in self.hands.items()
            for c in hand
            if pindex not in {self.our_player_index, player_index}
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
        self, player_index
    ) -> Dict[Tuple[int, int], List[int]]:
        candidates_list = self.all_candidates_list[player_index]
        orders = {}
        for i, candidates in enumerate(candidates_list):
            if len(candidates) == 1:
                singleton = list(candidates)[0]
                if singleton not in orders:
                    orders[singleton] = []
                orders[singleton].append(self.hands[player_index][i].order)
        return orders

    def get_doubleton_orders(self, player_index):
        candidates_list = self.all_candidates_list[player_index]
        orders = {}
        for i, candidates in enumerate(candidates_list):
            if len(candidates) == 2:
                doubleton_tup = tuple(
                    sorted([list(candidates)[0], list(candidates)[1]])
                )
                if doubleton_tup not in orders:
                    orders[doubleton_tup] = []
                orders[doubleton_tup].append(self.hands[player_index][i].order)
        return orders

    def get_tripleton_orders(self, player_index):
        candidates_list = self.all_candidates_list[player_index]
        orders = {}
        possible_tripleton_candidates = set()
        for i, candidates in enumerate(candidates_list):
            if len(candidates) in {2, 3}:
                for candidate in candidates:
                    possible_tripleton_candidates.add(candidate)

        for tripleton in itertools.combinations(possible_tripleton_candidates, 3):
            orders[tripleton] = []
            for i, candidates in enumerate(candidates_list):
                if not len(candidates.difference(set(tripleton))):
                    orders[tripleton].append(self.hands[player_index][i].order)
        return orders

    def _process_visible_cards(self):
        for player_index in range(self.num_players):
            candidates_list = self.all_candidates_list[player_index]
            fully_known_card_orders = self.get_fully_known_card_orders(player_index)
            for i, candidates in enumerate(candidates_list):
                removed_cards = set()
                for suit, rank in candidates:
                    copies_visible = self.get_copies_visible(player_index, suit, rank)
                    # copies visible is only for other players' hands and discard pile
                    # also incorporate information from my own hand
                    for (
                        fk_suit_index,
                        fk_rank,
                    ), orders in fully_known_card_orders.items():
                        for order in orders:
                            if order != self.hands[player_index][i].order and (
                                fk_suit_index,
                                fk_rank,
                            ) == (suit, rank):
                                copies_visible += 1
                                print(
                                    self.player_names[player_index]
                                    + ": See a copy of "
                                    + str((suit, rank))
                                    + " (order "
                                    + str(order)
                                    + ") elsewhere in my hand, not slot "
                                    + str(len(candidates_list) - i)
                                )

                    # TODO: handle reversed
                    # TODO: remove all of this debugging
                    elim1 = rank == 1 and copies_visible == 3
                    elim2 = rank == 5 and copies_visible == 1
                    elim3 = rank in {2, 3, 4} and copies_visible == 2
                    elim4 = (
                        SUITS[self.variant_name][suit] in DARK_SUIT_NAMES
                        and copies_visible == 1
                    )
                    if elim1 or elim2 or elim3 or elim4:
                        removed_cards.add((suit, rank))
                        print(
                            self.player_names[player_index]
                            + ": Removed candidate "
                            + str((suit, rank))
                            + " from slot "
                            + str(len(candidates_list) - i)
                        )

                candidates_list[i] = candidates_list[i].difference(removed_cards)

    def _process_doubletons(self):
        for player_index in range(self.num_players):
            candidates_list = self.all_candidates_list[player_index]
            doubleton_orders = self.get_doubleton_orders(player_index)
            for doubleton, orders in doubleton_orders.items():
                if len(orders) < 2:
                    continue

                first, second = doubleton
                firsts_visible = self.get_copies_visible(
                    player_index, first[0], first[1]
                )
                seconds_visible = self.get_copies_visible(
                    player_index, second[0], second[1]
                )
                num_of_firsts = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[first[1]]
                num_of_seconds = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[second[1]]
                if (
                    len(orders)
                    < num_of_firsts + num_of_seconds - firsts_visible - seconds_visible
                ):
                    continue

                for i, candidates in enumerate(candidates_list):
                    if self.hands[player_index][i].order not in orders:
                        p = self.player_names[player_index]
                        print(
                            f"{p}: Removed doubletons {first} and {second} "
                            f"from slot {len(candidates_list) - i}"
                        )
                        candidates_list[i] = candidates_list[i].difference(
                            {first, second}
                        )

    def _process_tripletons(self):
        for player_index in range(self.num_players):
            candidates_list = self.all_candidates_list[player_index]
            tripleton_orders = self.get_tripleton_orders(player_index)
            for tripleton, orders in tripleton_orders.items():
                if len(orders) < 3:
                    continue

                first, second, third = tripleton
                s1_vis = self.get_copies_visible(player_index, first[0], first[1])
                s2_vis = self.get_copies_visible(player_index, second[0], second[1])
                s3_vis = self.get_copies_visible(player_index, third[0], third[1])
                _1sts = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[first[1]]
                _2nds = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[second[1]]
                _3rds = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[third[1]]
                if len(orders) < _1sts + _2nds + _3rds - s1_vis - s2_vis - s3_vis:
                    continue

                for i, candidates in enumerate(candidates_list):
                    if self.hands[player_index][i].order not in orders:
                        p = self.player_names[player_index]
                        print(
                            f"{p}: Removed tripletons {first} and {second} and {third} "
                            f"from slot {len(candidates_list) - i}"
                        )
                        candidates_list[i] = candidates_list[i].difference(
                            {first, second, third}
                        )

    def process_visible_cards(self):
        for _ in range(3):
            self._process_visible_cards()
            self._process_doubletons()
            self._process_tripletons()

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
            )
            output += "\n  "
            for card in reversed(self.hands[i]):
                if (
                    card.order in self.rank_clued_card_orders
                    and self.color_clued_card_orders
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
        return card

    def handle_draw(self, player_index, order, suit_index, rank):
        new_card = Card(order=order, suit_index=suit_index, rank=rank)
        self.hands[player_index].append(new_card)
        self.all_candidates_list[player_index].append(get_all_cards(self.variant_name))
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

    def handle_clue(
        self,
        clue_giver: int,
        target_index: int,
        clue_type: int,
        clue_value: int,
        card_orders,
    ):
        raise NotImplementedError

    def get_cards_touched_dict(
        self, variant_name: str, target_index: int, clue_type_values
    ) -> Dict[Tuple[int, int, int], Set[Tuple[int, int]]]:
        target_hand = self.hands[target_index]
        clue_to_cards_touched = {}
        for clue_type, clue_value in clue_type_values:
            cards_touched = get_all_touched_cards(clue_type, clue_value, variant_name)
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


def test_get_num_available_color_clues():
    assert get_available_color_clues("No Variant") == [
        "Red",
        "Yellow",
        "Green",
        "Blue",
        "Purple",
    ]
    assert get_available_color_clues("6 Suits") == [
        "Red",
        "Yellow",
        "Green",
        "Blue",
        "Purple",
        "Teal",
    ]
    assert get_available_color_clues("Black (6 Suits)") == [
        "Red",
        "Yellow",
        "Green",
        "Blue",
        "Purple",
        "Black",
    ]
    assert get_available_color_clues("Pink (6 Suits)") == [
        "Red",
        "Yellow",
        "Green",
        "Blue",
        "Purple",
        "Pink",
    ]
    assert get_available_color_clues("Brown (6 Suits)") == [
        "Red",
        "Yellow",
        "Green",
        "Blue",
        "Purple",
        "Brown",
    ]
    assert get_available_color_clues("Pink & Brown (6 Suits)") == [
        "Red",
        "Yellow",
        "Green",
        "Blue",
        "Pink",
        "Brown",
    ]
    assert get_available_color_clues("Black & Pink (5 Suits)") == [
        "Red",
        "Green",
        "Blue",
        "Black",
        "Pink",
    ]
    assert get_available_color_clues("Omni (5 Suits)") == [
        "Red",
        "Yellow",
        "Green",
        "Blue",
    ]
    assert get_available_color_clues("Rainbow & Omni (5 Suits)") == [
        "Red",
        "Green",
        "Blue",
    ]
    assert get_available_color_clues("Rainbow & White (4 Suits)") == ["Red", "Blue"]
    assert get_available_color_clues("Null & Muddy Rainbow (4 Suits)") == [
        "Red",
        "Blue",
    ]
    assert get_available_color_clues("Null & Muddy Rainbow (4 Suits)") == [
        "Red",
        "Blue",
    ]
    assert get_available_color_clues("White & Null (3 Suits)") == ["Red"]
    assert get_available_color_clues("Omni & Muddy Rainbow (3 Suits)") == ["Red"]


def test_get_all_touched_cards():
    assert get_all_touched_cards(COLOR_CLUE, 1, "No Variant") == {
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "No Variant") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Rainbow (4 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Rainbow (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 3, "Pink (4 Suits)") == {
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Pink (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "White (4 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "White (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 3, "Brown (4 Suits)") == {
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Brown (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Muddy Rainbow (4 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Muddy Rainbow (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Light Pink (4 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Light Pink (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Omni (4 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Omni (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Null (4 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Null (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 1, "Rainbow & Omni (4 Suits)") == {
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Rainbow & Omni (4 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Dark Rainbow (5 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
        (4, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Pink (5 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
        (4, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Brown (5 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Cocoa Rainbow (5 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
        (4, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Cocoa Rainbow (5 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Gray Pink (5 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
        (4, 5),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Dark Omni (5 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
        (4, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Omni (5 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
        (4, 5),
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Null (5 Suits)") == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
    }
    assert get_all_touched_cards(COLOR_CLUE, 0, "Null & Prism (5 Suits)") == {
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (4, 1),
        (4, 4),
    }
    assert get_all_touched_cards(COLOR_CLUE, 1, "Null & Prism (5 Suits)") == {
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (4, 2),
        (4, 5),
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Null & Prism (5 Suits)") == {
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (4, 3),
    }


def test_game_state_playables_criticals():
    state = GameState()
    state.set_variant_name("Black (6 Suits)")
    state.stacks[2] += 1
    state.stacks[5] += 2
    state.discards = {(2, 1): 2, (2, 4): 1, (1, 2): 1, (3, 1): 2}
    assert sorted(state.playables) == [(0, 1), (1, 1), (2, 2), (3, 1), (4, 1), (5, 3)]
    assert sorted(state.criticals) == [
        (0, 5),
        (1, 2),
        (1, 5),
        (2, 4),
        (2, 5),
        (3, 1),
        (3, 5),
        (4, 5),
        (5, 1),
        (5, 2),
        (5, 3),
        (5, 4),
        (5, 5),
    ]


if __name__ == "__main__":
    np.random.seed(20000)
    variant_name = "Prism (5 Suits)"
    player_names = ["test0", "test1", "test2", "test3"]
    states = {
        player_name: GameState(variant_name, player_names, our_player_index)
        for our_player_index, player_name in enumerate(player_names)
    }
    deck = get_random_deck(variant_name)
    num_cards_per_player = {2: 5, 3: 5, 4: 4, 5: 4, 6: 3}[len(states)]
    order = 0

    for player_index, player_name in enumerate(states):
        for i in range(num_cards_per_player):
            card = deck.pop(0)
            for player_iterate in states:
                if player_iterate == player_name:
                    states[player_iterate].handle_draw(player_index, order, -1, -1)
                else:
                    states[player_iterate].handle_draw(
                        player_index, order, card.suit_index, card.rank
                    )
            order += 1

    state = states["test0"]
    state.stacks = [0, 2, 0, 0, 0]
    state.discards[(0, 1)] = 2
    state.discards[(4, 1)] = 2
    state.all_candidates_list[state.our_player_index][3] = {(0, 1), (3, 1), (4, 1)}
    state.all_candidates_list[state.our_player_index][2] = {(4, 1), (0, 1)}
    state.all_candidates_list[state.our_player_index][1] = {(4, 1), (3, 1), (0, 1)}
    state.all_candidates_list[state.our_player_index][0] = {(4, 1), (4, 5), (3, 1)}
    state.process_visible_cards()

    # state.handle_clue(clue_giver=3, target_index=0, clue_type=COLOR_CLUE, clue_value=3, card_orders=[3, 1])
    # state.handle_clue(clue_giver=3, target_index=0, clue_type=RANK_CLUE, clue_value=3, card_orders=[3, 1])
    # a = state.get_hat_residue(clue_giver=2, target_index=0, clue_type=RANK_CLUE, clue_value=2, card_orders=[0])

    state.print()
    print(state.get_legal_hat_clues())
    # print(a)
    2 / 0

    test_get_num_available_color_clues()
    test_get_all_touched_cards()
    test_game_state_playables_criticals()
