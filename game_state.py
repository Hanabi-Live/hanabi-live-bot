from constants import MAX_CLUE_NUM, COLOR_CLUE, RANK_CLUE

import os
import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import numpy as np
import itertools

variants_file = os.path.join(os.path.realpath(os.path.dirname(__file__)), "variants.json")
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
    "Dark Null"
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
    for color in ['Red', 'Yellow', 'Green', 'Blue', 'Purple', 'Teal', 'Black', 'Pink', 'Dark Pink', 'Brown', 'Dark Brown']:
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
                if suit in {available_color_clues[clue_value], "Rainbow", "Dark Rainbow", "Muddy Rainbow", "Cocoa Rainbow", "Omni", "Dark Omni"}:
                    cards.add((i, rank))
                if suit in {"Prism", "Dark Prism"} and (available_color_clues[clue_value], rank) in prism_touch:
                    cards.add((i, rank))
            elif clue_type == RANK_CLUE:
                if suit in {"Pink", "Dark Pink", "Light Pink", "Gray Pink", "Omni", "Dark Omni"}:
                    cards.add((i, rank))
                if suit not in {"Brown", "Dark Brown", "Muddy Rainbow", "Cocoa Rainbow", "Null", "Dark Null"} and clue_value == rank:
                    cards.add((i, rank))
    return cards

def get_all_non_touched_cards(clue_type: int, clue_value: int, variant_name: str):
    all_cards = get_all_cards(variant_name)
    return all_cards.difference(get_all_touched_cards(clue_type, clue_value, variant_name))

def is_brownish_pinkish(variant_name):
    num_suits = len(SUITS[variant_name])
    for rank in range(1,6):
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

def get_candidates_list_str(candidates_list, variant_name: str, actual_hand = None):
    output = ""
    
    for rank in range(1, 6):
        output += "\n"
        for hand_order, candidates in enumerate(candidates_list):
            output += "  "
            for i, suit in enumerate(SUITS[variant_name]):
                if (i, rank) in candidates:
                    if actual_hand is not None:
                        actual_card = actual_hand[hand_order]
                        output += "x" if (i == actual_card.suit_index) and (rank == actual_card.rank) else "*"
                    else:
                        output += "*"
                else:
                    output += "."
        
    return output

def get_non_playful_mod_table(variant_name, preferred_modulus=None):
    # trash is marked as (0, 0)
    # first good 1 is marked as (-1, 1), second good 1 as (-2, 1), etc.
    num_suits = len(SUITS[variant_name])
    all_cards = get_all_cards(variant_name)
    if num_suits == 6:
        if len(set(SUITS[variant_name]).intersection(set(DARK_SUIT_NAMES))) < 2:
            mod_table = {
                0: {
                    0: [(-1,1)], 1: [(-2,1)], 2: [(-3,1)], 3: [(-4,1)],
                    4: [(-5,1)], 5: [(-6,1)], 6: [(0,2),(2,2)], 7: [(1,2),(3,2)],
                    8: [(4,2),(0,3)], 9: [(1,3),(3,3)], 10: [(2,4),(1,5)], 11: [(4,4),(0,5)],
                    12: [(5,2),(2,3),(0,4)], 13: [(5,3),(1,4),(2,5)], 14: [(4,3),(5,4),(3,5)], 15: [(3,4),(4,5),(5,5)]
                },
                1: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                    4: [(-4,1)], 5: [(-5,1)], 6: [(0,2),(2,2)], 7: [(1,2),(3,2)],
                    8: [(4,2),(0,3)], 9: [(1,3),(3,3)], 10: [(2,4),(1,5)], 11: [(4,4),(0,5)],
                    12: [(5,2),(2,3),(0,4)], 13: [(5,3),(1,4),(2,5)], 14: [(4,3),(5,4),(3,5)], 15: [(3,4),(4,5),(5,5)]
                },
                2: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                    4: [(-4,1)], 5: [(0,2),(2,2)], 6: [(1,2),(3,2)], 7: [(4,2),(0,3)],
                    8: [(1,3),(3,3)], 9: [(2,3),(0,4)], 10: [(2,4),(1,5)], 11: [(4,4),(0,5)],
                    12: [(5,2),(1,4)], 13: [(5,3),(2,5)], 14: [(4,3),(5,4),(3,5)], 15: [(3,4),(4,5),(5,5)]
                },
                3: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                    4: [(0,2),(2,2)], 5: [(1,2),(3,2)], 6: [(4,2),(0,3)], 7: [(1,3),(3,3)],
                    8: [(2,3),(0,4)], 9: [(4,3),(2,4)], 10: [(4,4),(0,5)], 11: [(3,4),(1,5)], 
                    12: [(5,2),(1,4)], 13: [(5,3),(2,5)], 14: [(5,4),(3,5)], 15: [(4,5),(5,5)]
                },
                4: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(0,2),(2,3)],
                    4: [(1,2),(3,3)], 5: [(2,2),(1,3)], 6: [(3,2),(4,3)], 7: [(4,2),(0,3)],
                    8: [(0,4),(2,4)], 9: [(1,4),(2,5)], 10: [(4,4),(0,5)], 11: [(3,4),(1,5)], 
                    12: [(5,2)], 13: [(5,3)], 14: [(5,4),(3,5)], 15: [(4,5),(5,5)]
                },
                5: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(0,2),(2,3)], 3: [(1,2),(3,3)],
                    4: [(2,2),(1,3)], 5: [(3,2),(4,3)], 6: [(4,2),(0,3)], 7: [(0,4),(4,5)],
                    8: [(1,4),(2,5)], 9: [(2,4),(1,5)], 10: [(3,4),(0,5)], 11: [(4,4)], 
                    12: [(5,2)], 13: [(5,3)], 14: [(5,4),(3,5)], 15: [(5,5)]
                },
                6: {
                    0: [(0,0)], 1: [(0,2),(2,3)], 2: [(1,2),(3,3)], 3: [(2,2),(1,3)],
                    4: [(3,2),(4,3)], 5: [(4,2),(0,3)], 6: [(0,4)], 7: [(1,4),(2,5)],
                    8: [(2,4),(1,5)], 9: [(3,4),(0,5)], 10: [(4,4)], 11: [(4,5)], 
                    12: [(5,2)], 13: [(5,3)], 14: [(5,4),(3,5)], 15: [(5,5)]
                }
            }
        else:
            raise NotImplementedError
    if num_suits == 5:
        if preferred_modulus == 16:
            mod_table = {
                0: {
                    0: [(-1,1)], 1: [(-2,1)], 2: [(-3,1)], 3: [(-4,1)],
                    4: [(-5,1)], 5: [(0,2),(2,2)], 6: [(1,2),(3,2)], 7: [(4,2)],
                    8: [(0,3),(2,3)], 9: [(1,3),(3,3)], 10: [(4,3)], 11: [(2,4),(0,5)],
                    12: [(1,4),(3,5)], 13: [(3,4),(1,5)], 14: [(4,4),(2,5)], 15: [(0,4),(4,5)],
                },
                1: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                    4: [(-4,1)], 5: [(0,2),(2,2)], 6: [(1,2),(3,2)], 7: [(4,2)],
                    8: [(0,3),(2,3)], 9: [(1,3),(3,3)], 10: [(4,3)], 11: [(2,4),(0,5)],
                    12: [(1,4),(3,5)], 13: [(3,4),(1,5)], 14: [(4,4),(2,5)], 15: [(0,4),(4,5)],
                },
                2: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                    4: [(0,2),(2,3)], 5: [(2,2),(1,3)], 6: [(1,2),(3,2)], 7: [(4,2)],
                    8: [(0,3),(3,4)], 9: [(3,3),(1,4)], 10: [(4,3)], 11: [(2,4),(0,5)],
                    12: [(1,5)], 13: [(3,5)], 14: [(4,4),(2,5)], 15: [(0,4),(4,5)]
                },
                3: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(0,2),(2,3)],
                    4: [(2,2),(1,3)], 5: [(1,2),(3,3)], 6: [(3,2),(0,3)], 7: [(4,2)],
                    8: [(4,3)], 9: [(1,4)], 10: [(3,4)], 11: [(2,4),(0,5)],
                    12: [(1,5)], 13: [(3,5)], 14: [(4,4),(2,5)], 15: [(0,4),(4,5)]
                },
                4: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(0,2),(2,3)], 3: [(2,2),(1,3)],
                    4: [(1,2),(3,3)], 5: [(3,2),(0,3)], 6: [(4,2)], 7: [(4,3)],
                    8: [(1,4)], 9: [(2,4)], 10: [(3,4)], 11: [(0,5)],
                    12: [(1,5)], 13: [(3,5)], 14: [(4,4),(2,5)], 15: [(0,4),(4,5)]
                },
                5: {
                    0: [(0,0)], 1: [(0,2),(2,3)], 2: [(2,2),(1,3)], 3: [(1,2),(3,3)],
                    4: [(3,2),(0,3)], 5: [(4,2)], 6: [(4,3)], 7: [(0,4)],
                    8: [(1,4)], 9: [(2,4)], 10: [(3,4)], 11: [(0,5)],
                    12: [(1,5)], 13: [(3,5)], 14: [(4,4),(2,5)], 15: [(4,5)]
                }
            }
        else:
            mod_table = {
                0: {
                    0: [(-1,1)], 1: [(-2,1)], 2: [(-3,1)], 3: [(-4,1)],
                    4: [(-5,1)], 5: [(0,2),(1,2),(2,2)], 6: [(3,2),(4,2)], 7: [(0,3),(2,3),(3,4)],
                    8: [(1,3),(3,3),(2,4)], 9: [(4,3),(1,4),(0,5)], 10: [(4,4),(1,5),(2,5)], 11: [(0,4),(3,5),(4,5)]
                },
                1: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                    4: [(-4,1)], 5: [(0,2),(1,2),(2,2)], 6: [(3,2),(4,2)], 7: [(0,3),(2,3),(3,4)],
                    8: [(1,3),(3,3),(2,4)], 9: [(4,3),(1,4),(0,5)], 10: [(4,4),(1,5),(2,5)], 11: [(0,4),(3,5),(4,5)]
                },
                2: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                    4: [(0,2),(1,2),(2,2)], 5: [(3,2),(4,2)], 6: [(0,3),(2,3)], 7: [(1,3),(3,4)],
                    8: [(3,3),(2,4)], 9: [(4,3),(1,4),(0,5)], 10: [(4,4),(1,5),(2,5)], 11: [(0,4),(3,5),(4,5)]
                },
                3: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(0,2),(2,2)],
                    4: [(1,2),(2,3)], 5: [(3,2),(0,3)], 6: [(4,2),(3,3)], 7: [(1,3),(3,4)],
                    8: [(2,4),(1,5)], 9: [(4,3),(1,4),(0,5)], 10: [(4,4),(2,5)], 11: [(0,4),(3,5),(4,5)]
                },
                4: {
                    0: [(0,0)], 1: [(-1,1)], 2: [(0,2),(2,2)], 3: [(1,2),(2,3)],
                    4: [(3,2),(0,3)], 5: [(4,2),(3,3)], 6: [(1,3),(3,4)], 7: [(2,4),(1,5)],
                    8: [(1,4),(3,5)], 9: [(4,3),(0,5)], 10: [(4,4),(2,5)], 11: [(0,4),(4,5)]
                },
                5: {
                    0: [(0,0)], 1: [(0,2),(2,3)], 2: [(1,2),(3,3)], 3: [(2,2),(1,3)],
                    4: [(3,2),(0,3)], 5: [(4,2)], 6: [(2,4),(1,5)], 7: [(1,4),(3,5)],
                    8: [(3,4),(0,5)], 9: [(4,3)], 10: [(4,4),(2,5)], 11: [(0,4),(4,5)]
                }
            }
    if num_suits == 4:
        mod_table = {
            0: {
                0: [(-1,1)], 1: [(-2,1)], 2: [(-3,1)], 3: [(-4,1)],
                4: [(0,2),(1,2)], 5: [(2,2),(0,3)], 6: [(3,2),(1,3)], 7: [(2,3),(0,4)],
                8: [(3,3),(1,4)], 9: [(2,4),(0,5)], 10: [(3,4),(1,5)], 11: [(2,5),(3,5)]
            },
            1: {
                0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(-3,1)],
                4: [(0,2),(1,2)], 5: [(2,2),(0,3)], 6: [(3,2),(1,3)], 7: [(2,3),(0,4)],
                8: [(3,3),(1,4)], 9: [(2,4),(0,5)], 10: [(3,4),(1,5)], 11: [(2,5),(3,5)]
            },
            2: {
                0: [(0,0)], 1: [(-1,1)], 2: [(-2,1)], 3: [(0,2),(1,2)],
                4: [(2,2),(0,3)], 5: [(3,2),(1,3)], 6: [(2,3)], 7: [(3,3)],
                8: [(0,4),(1,5)], 9: [(1,4),(2,5)], 10: [(2,4),(3,5)], 11: [(3,4),(0,5)]
            },
            3: {
                0: [(0,0)], 1: [(-1,1)], 2: [(0,2),(1,2)], 3: [(2,2),(0,3)],
                4: [(3,2),(1,3)], 5: [(2,3)], 6: [(3,3)], 7: [(0,4)],
                8: [(1,4),(2,5)], 9: [(2,4),(3,5)], 10: [(3,4),(0,5)], 11: [(1,5)]
            },
            4: {
                0: [(0,0)], 1: [(0,2),(1,3)], 2: [(1,2),(2,3)], 3: [(2,2),(3,3)],
                4: [(3,2),(0,3)], 5: [(0,4)], 6: [(1,4)], 7: [(2,4)],
                8: [(3,4),(0,5)], 9: [(1,5)], 10: [(2,5)], 11: [(3,5)]
            }
        }
    if num_suits == 3:
        raise ValueError

    return mod_table

def get_starting_pace(num_players: int, variant_name: str):
    num_suits = len(SUITS[variant_name])
    base_starting_pace = {
        6: 18,
        5: 15,
        4: 18,
        3: 18,
        2: 22
    }[num_players]
    num_dark_suits = len({x for x in SUITS[variant_name] if x in DARK_SUIT_NAMES})
    return base_starting_pace - (6 - num_suits) * 5 - num_dark_suits * 5

class GameState:
    def __init__(self, variant_name, player_names, our_player_index):
        self.set_variant_name(variant_name, len(player_names))
        self.player_names: List[str] = player_names
        self.our_player_index: int = our_player_index
        self.current_player_index = 0

        # Initialize the hands for each player (an array of cards)
        self.hands: Dict[int, List[Card]] = {}
        self.all_candidates_list: Dict[int, List[Set[Tuple[int, int]]]] = {}
        for i in range(len(player_names)):
            self.hands[i] = []
            self.all_candidates_list[i] = []

        self.clue_tokens: int = MAX_CLUE_NUM
        self.bombs: int = 0
        self.rank_clued_card_orders: Dict[int, List[int]] = {}
        self.color_clued_card_orders: Dict[int, List[int]] = {}
        self.hat_clued_card_orders: Set[int] = set()
        self.stacks: List[int] = [0] * len(SUITS[variant_name])
        self.discards: Dict[Tuple[int, int], int] = {}    # keys are tuples of (suit_index, rank)
        self.turn: int = 0
        self.notes: Dict[int, str] = {}

    @property
    def num_players(self):
        return len(self.player_names)

    @property
    def our_player_name(self):
        return self.player_names[self.our_player_index]

    @property
    def playables(self):
        # TODO: handle reversed
        return set([(suit, stack + 1) for suit, stack in enumerate(self.stacks)])

    @property
    def score_pct(self):
        return sum(self.stacks) / (5 * len(self.stacks))

    @property
    def criticals(self):
        # TODO: handle reversed
        fives = set([(suit, 5) for suit in range(len(self.stacks))])
        dark_suits = set([
            (suit, i) for i in range(1, 6)
            for suit, suit_name in enumerate(SUITS[self.variant_name]) if suit_name in DARK_SUIT_NAMES
        ])
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
    def trash(self):
        # TODO: handle reversed
        # TODO: maybe handle the case where if all copies of a card were discarded then the rest is trash
        trash_cards = set()
        for suit, stack in enumerate(self.stacks):
            for i in range(stack):
                trash_cards.add((suit, i + 1))
        return trash_cards

    @property
    def pace(self):
        return get_starting_pace(self.num_players, self.variant_name) - sum(self.discards.values())

    @property
    def num_cards_in_deck(self):
        total_cards = len(get_all_cards_with_multiplicity(self.variant_name))
        cards_dealt = {2: 10, 3: 15, 4: 16, 5: 20, 6: 18}[self.num_players]
        return total_cards - cards_dealt - sum(self.discards.values()) - sum(self.stacks)

    @property
    def our_hand(self):
        return self.hands[self.our_player_index]

    @property
    def our_candidates(self):
        return self.all_candidates_list[self.our_player_index]

    @property
    def num_1s_played(self):
        return sum([x > 0 for x in self.stacks])

    @property
    def order_to_index(self):
        result = {}
        for player_index, hand in self.hands.items():
            for i, card in enumerate(hand):
                result[card.order] = (player_index, i)
        return result

    def get_candidates(self, order):
        player_index, i = self.order_to_index[order]
        return self.all_candidates_list[player_index][i]

    def get_card(self, order):
        player_index, i = self.order_to_index[order]
        return self.hands[player_index][i]

    def is_playable(self, candidates):
        return not len(candidates.difference(self.playables))

    def is_trash(self, candidates):
        return not len(candidates.difference(self.trash))

    def is_critical(self, candidates):
        return not len(candidates.difference(self.criticals))

    def get_all_other_players_cards(self, player_index=None):
        return {
            (c.suit_index, c.rank)
            for pindex, hand in self.hands.items() for c in hand
            if pindex not in {self.our_player_index, player_index}
        }

    def get_all_other_players_hat_clued_cards(self, player_index=None, no_singletons=False):
        if no_singletons:
            return {
                (c.suit_index, c.rank)
                for pindex, hand in self.hands.items() for i, c in enumerate(hand)
                if pindex not in {self.our_player_index, player_index}
                and c.order in self.hat_clued_card_orders
                and len(self.all_candidates_list[pindex][i]) > 1
            }
        else:
            return {
                (c.suit_index, c.rank)
                for pindex, hand in self.hands.items() for c in hand
                if pindex not in {self.our_player_index, player_index}
                and c.order in self.hat_clued_card_orders
            }

    def set_variant_name(self, variant_name: str, num_players: int):
        self.variant_name = variant_name
        self.stacks = [0] * len(SUITS[self.variant_name])
        if num_players == 4:
            self.mod_table = get_non_playful_mod_table(variant_name, preferred_modulus=12)
        elif num_players == 5:
            self.mod_table = get_non_playful_mod_table(variant_name, preferred_modulus=16)
        else:
            raise NotImplementedError

    def get_copies_visible(self, player_index, suit, rank):
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

    def get_fully_known_card_orders(self, player_index):
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
                doubleton_tup = tuple(sorted([list(candidates)[0], list(candidates)[1]]))
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
                for (suit, rank) in candidates:
                    copies_visible = self.get_copies_visible(player_index, suit, rank)
                    # copies visible is only for other players' hands and discard pile
                    # also incorporate information from my own hand
                    for (fk_suit_index, fk_rank), orders in fully_known_card_orders.items():
                        for order in orders:
                            if order != self.hands[player_index][i].order and (fk_suit_index, fk_rank) == (suit, rank):
                                copies_visible += 1
                                print(self.player_names[player_index] + ': See a copy of ' + str((suit, rank)) + ' (order ' + str(order) + ') elsewhere in my hand, not slot ' + str(len(candidates_list) - i))

                    # TODO: handle reversed
                    # TODO: remove all of this debugging
                    elim1 = (rank == 1 and copies_visible == 3)
                    elim2 = (rank == 5 and copies_visible == 1)
                    elim3 = (rank in {2, 3, 4} and copies_visible == 2)
                    elim4 = (SUITS[self.variant_name][suit] in DARK_SUIT_NAMES and copies_visible == 1)
                    if elim1 or elim2 or elim3 or elim4:
                        removed_cards.add((suit, rank))
                        print(self.player_names[player_index] + ': Removed candidate ' + str((suit, rank)) + ' from slot ' + str(len(candidates_list) - i))

                candidates_list[i] = candidates_list[i].difference(removed_cards)

    def _process_doubletons(self):
        for player_index in range(self.num_players):
            candidates_list = self.all_candidates_list[player_index]
            doubleton_orders = self.get_doubleton_orders(player_index)
            for doubleton, orders in doubleton_orders.items():
                if len(orders) < 2:
                    continue

                first, second = doubleton
                firsts_visible = self.get_copies_visible(player_index, first[0], first[1])
                seconds_visible = self.get_copies_visible(player_index, second[0], second[1])
                num_of_firsts = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[first[1]]
                num_of_seconds = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[second[1]]
                if len(orders) < num_of_firsts + num_of_seconds - firsts_visible - seconds_visible:
                    continue

                for i, candidates in enumerate(candidates_list):
                    if self.hands[player_index][i].order not in orders:
                        print(self.player_names[player_index] + ': Removed doubleton candidates ' + str(first) + ' and ' + str(second) + ' from slot ' + str(len(candidates_list) - i))
                        candidates_list[i] = candidates_list[i].difference({first, second})

    def _process_tripletons(self):
        for player_index in range(self.num_players):
            candidates_list = self.all_candidates_list[player_index]
            tripleton_orders = self.get_tripleton_orders(player_index)
            for tripleton, orders in tripleton_orders.items():
                if len(orders) < 3:
                    continue

                first, second, third = tripleton
                firsts_visible = self.get_copies_visible(player_index, first[0], first[1])
                seconds_visible = self.get_copies_visible(player_index, second[0], second[1])
                thirds_visible = self.get_copies_visible(player_index, third[0], third[1])
                num_of_firsts = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[first[1]]
                num_of_seconds = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[second[1]]
                num_of_thirds = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}[third[1]]
                if len(orders) < num_of_firsts + num_of_seconds + num_of_thirds - firsts_visible - seconds_visible - thirds_visible:
                    continue

                for i, candidates in enumerate(candidates_list):
                    if self.hands[player_index][i].order not in orders:
                        print(self.player_names[player_index] + ': Removed tripleton candidates ' + str(first) + ' and ' + str(second) + ' and ' + str(third) + ' from slot ' + str(len(candidates_list) - i))
                        candidates_list[i] = candidates_list[i].difference({first, second, third})

    def process_visible_cards(self):
        for _ in range(3):
            self._process_visible_cards()
            self._process_doubletons()
            self._process_tripletons()

    def get_rightmost_unnumbered_card(self, player_index):
        for card in self.hands[player_index]:    # iterating oldest to newest
            if card.order not in self.rank_clued_card_orders:
                return card
        return None

    def get_rightmost_uncolored_card(self, player_index):
        for card in self.hands[player_index]:    # iterating oldest to newest
            if card.order not in self.color_clued_card_orders:
                return card
        return None

    def get_leftmost_non_hat_clued_card(self, player_index):
        for j in range(len(self.hands[player_index])):
            card = self.hands[player_index][-j-1]
            if card.order not in self.hat_clued_card_orders:
                return card
        return None

    def print(self):
        output = "\nVariant: " + self.variant_name + ", POV: " + self.player_names[self.our_player_index] + "\n"
        output += "Turn: " + str(self.turn + 1) + ", currently on " + self.player_names[self.current_player_index] + "\n"
        output += "Clues: " + str(self.clue_tokens) + ", Bombs: " + str(self.bombs) + ", Pace: " + str(self.pace) + ", Cards: " + str(self.num_cards_in_deck) + "\n"
        output += "Stacks: " + ", ".join([
            suit_name + " " + str(self.stacks[i])
            for i, suit_name in enumerate(SUITS[self.variant_name])
        ]) + "\n"

        output += "\n"
        for i, name in enumerate(self.player_names):
            candidates_list = self.all_candidates_list[i]
            output += name + "\nOrders: " + ", ".join([str(card.order) for card in reversed(self.hands[i])])
            output += "\nNotes: " + ", ".join(["'" + self.notes.get(card.order, "") + "'" for card in reversed(self.hands[i])])
            output += get_candidates_list_str(
                list(reversed(candidates_list)), self.variant_name, list(reversed(self.hands[i]))
            )
            output += "\n  "
            for card in reversed(self.hands[i]):
                output += ("R" if card.order in self.rank_clued_card_orders else " ")
                output += ("C" if card.order in self.color_clued_card_orders else " ")
                output += ("H" if card.order in self.hat_clued_card_orders else " ")
                output += " " * (len(SUITS[self.variant_name]) - 1)
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

        if card_index is None:
            raise ValueError(
                "error: unable to find card with order " + str(order) + " in"
                "the hand of player " + str(player_index)
            )

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

    @property
    def mod_base(self):
        return max(self.mod_table[0]) + 1

    @property
    def num_residues_per_player(self):
        return int(self.mod_base / (self.num_players - 1))

    @property
    def identity_to_residue(self):
        result = {}
        trash_residue = 0
        for residue, identities in self.mod_table[self.num_1s_played].items():
            # there exist "fake" or "substitute" identities
            # these are (0, 0), (-1, 1), (-2, 1), etc.
            for identity in identities:
                if identity[1] == 1:
                    assert identity[0] < 0
                    ones_not_played = [
                        i for i, stack in enumerate(self.stacks) if stack == 0
                    ]
                    ones_mapping = {
                        (-i-1, 1): (suit_index, 1)
                        for i, suit_index in enumerate(ones_not_played)
                    }
                    result[ones_mapping[identity]] = residue
                elif identity != (0, 0):
                    result[identity] = residue
                else:
                    trash_residue = residue

        for (suit_index, rank) in self.trash:
            result[(suit_index, rank)] = trash_residue

        return result

    @property
    def residue_to_identities(self):
        result = {}
        for identity, residue in self.identity_to_residue.items():
            if residue not in result:
                result[residue] = set()
            result[residue].add(identity)
        return result

    def handle_clue(self, clue_giver: int, target_index: int, clue_type: int, clue_value: int, card_orders):
        all_cards_touched_by_clue = get_all_touched_cards(clue_type, clue_value, self.variant_name)
        touched_cards = []
        candidates_list = self.all_candidates_list[target_index]
        order_to_index = self.order_to_index

        for i, card in enumerate(self.hands[target_index]):
            if card.order in card_orders:
                touched_cards.append(card)
                candidates_list[i] = candidates_list[i].intersection(all_cards_touched_by_clue)
            else:
                candidates_list[i] = candidates_list[i].difference(all_cards_touched_by_clue)

        identity_to_residue = self.identity_to_residue
        residue_to_identities = self.residue_to_identities
        hat_residue = self.get_hat_residue(clue_giver, target_index, clue_type, clue_value, card_orders)

        sum_of_others_residues = 0
        for player_index, hand in self.hands.items():
            if player_index in {self.our_player_index, clue_giver}:
                continue

            left_non_hat_clued = self.get_leftmost_non_hat_clued_card(player_index)
            if left_non_hat_clued is None:
                continue

            other_residue = identity_to_residue[(
                left_non_hat_clued.suit_index,
                left_non_hat_clued.rank
            )]
            print(self.player_names[player_index] + ' ' + str(left_non_hat_clued) + ' has residue ' + str(other_residue))
            sum_of_others_residues += other_residue

            _, i = order_to_index[left_non_hat_clued.order]
            new_candidates = self.all_candidates_list[player_index][i].intersection(
                residue_to_identities[other_residue]
            )
            self.all_candidates_list[player_index][i] = new_candidates

            self.write_note(left_non_hat_clued.order, note="", candidates=new_candidates)
            self.hat_clued_card_orders.add(left_non_hat_clued.order)

        if self.our_player_index != clue_giver:
            my_residue = (hat_residue - sum_of_others_residues) % self.mod_base
            print('My (' + self.our_player_name + ') residue = ' + str(my_residue))
            left_non_hat_clued = self.get_leftmost_non_hat_clued_card(self.our_player_index)
            if left_non_hat_clued is not None:
                _, i = order_to_index[left_non_hat_clued.order]
                new_candidates = self.all_candidates_list[self.our_player_index][i].intersection(
                    residue_to_identities[my_residue]
                )
                self.all_candidates_list[self.our_player_index][i] = new_candidates
                self.write_note(left_non_hat_clued.order, note="", candidates=new_candidates)
                self.hat_clued_card_orders.add(left_non_hat_clued.order)

        # mark clued last since we want hat logic to act on what was in the hand prior to the clue
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

    def get_leftmost_non_hat_clued_cards(self):
        result = []
        for player_index, hand in self.hands.items():
            if player_index == self.our_player_index:
                continue
            lnhc = self.get_leftmost_non_hat_clued_card(player_index)
            result.append(lnhc)
        return result

    def get_cards_touched_dict(self, variant_name: str, target_index: int, clue_type_values):
        target_hand = self.hands[target_index]
        clue_to_cards_touched = {}
        for (clue_type, clue_value) in clue_type_values:
            cards_touched = get_all_touched_cards(clue_type, clue_value, variant_name)
            cards_touched_in_target_hand = [
                card for card in target_hand
                if (card.suit_index, card.rank) in cards_touched
            ]
            if len(cards_touched_in_target_hand):
                clue_to_cards_touched[(clue_type, clue_value)] = cards_touched_in_target_hand
        return {
            (clue_value, clue_type, target_index): cards_touched
            for (clue_type, clue_value), cards_touched in clue_to_cards_touched.items()
        }

    def get_special_hat_clues(self, variant_name: str, target_index: int, clue_mapping_only=False):
        target_hand = self.hands[target_index]
        dct = {}
        if variant_name == "Valentine Mix (6 Suits)":
            dct = {
                0: [(RANK_CLUE, 5), (RANK_CLUE, 1)],
                1: [(RANK_CLUE, 2), (COLOR_CLUE, 0)],
                2: [(COLOR_CLUE, 1), (RANK_CLUE, 3)],
                3: [(RANK_CLUE, 4)],
            }

        if clue_mapping_only:
            return dct if len(dct) else None

        return {
            raw_residue: self.get_cards_touched_dict(variant_name, target_index, clue_type_values)
            for raw_residue, clue_type_values in dct.items()
        } if len(dct) else None

    def get_legal_hat_clues(self):
        sum_of_residues = 0
        num_residues = self.num_residues_per_player

        identity_to_residue = self.identity_to_residue
        for player_index, hand in self.hands.items():
            if player_index == self.our_player_index:
                continue
            lnhc = self.get_leftmost_non_hat_clued_card(player_index)
            if lnhc is None:
                continue

            sum_of_residues += identity_to_residue[(lnhc.suit_index, lnhc.rank)]

        sum_of_residues = sum_of_residues % self.mod_base
        target_index = (self.our_player_index + 1 + (sum_of_residues // num_residues)) % self.num_players
        raw_residue = sum_of_residues % num_residues
        target_hand = self.hands[target_index]

        assert target_index != self.our_player_index
        print('Evaluating legal hat clues - sum of residues =', sum_of_residues, 'target_index', target_index)
        maybe_special_hat_clues = self.get_special_hat_clues(self.variant_name, target_index)
        if maybe_special_hat_clues is not None:
            return maybe_special_hat_clues[raw_residue]

        if num_residues == 4:
            if raw_residue in {0, 1}:
                if is_brownish_pinkish(self.variant_name):
                    if raw_residue == 0:
                        return self.get_cards_touched_dict(
                            self.variant_name,
                            target_index,
                            [(RANK_CLUE, 2), (RANK_CLUE, 3), (RANK_CLUE, 5)]
                        )
                    else:
                        return self.get_cards_touched_dict(
                            self.variant_name,
                            target_index,
                            [(RANK_CLUE, 1), (RANK_CLUE, 4)]
                        )
                else:
                    rightmost_unnumbered = self.get_rightmost_unnumbered_card(target_index)
                    # iterate over rank clues
                    # TODO: special 1s/5s
                    rank_to_cards_touched = {}
                    for clue_value in range(1, 6):
                        cards_touched = get_all_touched_cards(RANK_CLUE, clue_value, self.variant_name)
                        cards_touched_in_target_hand = [
                            card for card in target_hand
                            if (card.suit_index, card.rank) in cards_touched
                        ]
                        if len(cards_touched_in_target_hand):
                            rank_to_cards_touched[clue_value] = cards_touched_in_target_hand

                    if rightmost_unnumbered is None:
                        clue_rank = (min(rank_to_cards_touched) if raw_residue == 0 else max(rank_to_cards_touched))
                        return {
                            (clue_value, RANK_CLUE, target_index): cards_touched
                            for clue_value, cards_touched in rank_to_cards_touched.items()
                            if clue_value == clue_rank
                        }
                    else:
                        if raw_residue == 0:
                            return {
                                (clue_value, RANK_CLUE, target_index): cards_touched
                                for clue_value, cards_touched in rank_to_cards_touched.items()
                                if rightmost_unnumbered in cards_touched
                            }
                        else:
                            return {
                                (clue_value, RANK_CLUE, target_index): cards_touched
                                for clue_value, cards_touched in rank_to_cards_touched.items()
                                if rightmost_unnumbered not in cards_touched
                            }

            elif raw_residue in {2, 3}:
                if is_whiteish_rainbowy(self.variant_name):
                    num_colors = len(get_available_color_clues(self.variant_name))
                    if num_colors in {2,4,5,6}:
                        color_to_cards_touched = {}
                        clue_values = range(num_colors // 2) if raw_residue == 2 else range(num_colors // 2, num_colors)
                        for clue_value in clue_values:
                            cards_touched = get_all_touched_cards(COLOR_CLUE, clue_value, self.variant_name)
                            cards_touched_in_target_hand = [
                                card for card in target_hand
                                if (card.suit_index, card.rank) in cards_touched
                            ]
                            if len(cards_touched_in_target_hand):
                                color_to_cards_touched[clue_value] = cards_touched_in_target_hand

                        return {
                            (clue_value, COLOR_CLUE, target_index): cards_touched
                            for clue_value, cards_touched in color_to_cards_touched.items()
                        }
                    else:
                        raise NotImplementedError
                else: 
                    rightmost_uncolored = self.get_rightmost_uncolored_card(target_index)
                    # iterate over color clues
                    color_to_cards_touched = {}
                    for clue_value, _ in enumerate(get_available_color_clues(self.variant_name)):
                        cards_touched = get_all_touched_cards(COLOR_CLUE, clue_value, self.variant_name)
                        cards_touched_in_target_hand =  [
                            card for card in target_hand
                            if (card.suit_index, card.rank) in cards_touched
                        ]
                        if len(cards_touched_in_target_hand):
                            color_to_cards_touched[clue_value] = cards_touched_in_target_hand

                    if rightmost_uncolored is None:
                        clue_color = (min(color_to_cards_touched) if raw_residue == 2 else max(color_to_cards_touched))
                        return {
                            (clue_value, COLOR_CLUE, target_index): cards_touched
                            for clue_value, cards_touched in color_to_cards_touched.items()
                            if clue_value == clue_color
                        }
                    else:
                        if raw_residue == 2:
                            return {
                                (clue_value, COLOR_CLUE, target_index): cards_touched
                                for clue_value, cards_touched in color_to_cards_touched.items()
                                if rightmost_uncolored in cards_touched
                            }
                        else:
                            return {
                                (clue_value, COLOR_CLUE, target_index): cards_touched
                                for clue_value, cards_touched in color_to_cards_touched.items()
                                if rightmost_uncolored not in cards_touched
                            }

        elif num_residues == 3:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def get_hat_residue(self, clue_giver: int, target_index: int, clue_type: int, clue_value: int, card_orders):
        # TODO: depends on variant
        num_residues = self.num_residues_per_player
        rightmost_unnumbered = self.get_rightmost_unnumbered_card(target_index)
        rightmost_uncolored = self.get_rightmost_uncolored_card(target_index)

        clue_mappings = self.get_special_hat_clues(
            self.variant_name, target_index, clue_mapping_only=True
        )
        if clue_mappings is not None:
            for raw_residue, clue_type_values in clue_mappings.items():
                for (_type, _value) in clue_type_values:
                    if clue_type == _type and clue_value == _value:
                        return raw_residue + ((target_index - clue_giver - 1) % self.num_players) * num_residues

        if num_residues == 4:
            if clue_type == RANK_CLUE:
                if is_brownish_pinkish(self.variant_name):
                    raw_residue = 0 if clue_value in {2,3,5} else 1
                else:
                    if rightmost_unnumbered is None:
                        all_ranks_clued = []
                        for card in self.hands[target_index]:
                            all_ranks_clued += self.rank_clued_card_orders[card.order]

                        if clue_value == min(all_ranks_clued):
                            raw_residue = 0
                        elif clue_value == max(all_ranks_clued):
                            raw_residue = 1
                        else:
                            raise IndentationError
                    else:
                        if rightmost_unnumbered.order in card_orders:
                            raw_residue = 0
                        else:
                            raw_residue = 1
            elif clue_type == COLOR_CLUE:
                if is_whiteish_rainbowy(self.variant_name):
                    num_colors = len(get_available_color_clues(self.variant_name))
                    if num_colors in {2,4,5,6}:
                        raw_residue = 2 if clue_value in range(num_colors // 2) else 3
                    else:
                        raise NotImplementedError
                else:
                    if rightmost_uncolored is None:
                        all_colors_clued = []
                        for card in self.hands[target_index]:
                            all_colors_clued += self.color_clued_card_orders[card.order]

                        if clue_value == min(all_colors_clued):
                            raw_residue = 2
                        elif clue_value == max(all_colors_clued):
                            raw_residue = 3
                        else:
                            raise IndentationError
                    else:
                        if rightmost_uncolored.order in card_orders:
                            raw_residue = 2
                        else:
                            raw_residue = 3
            else:
                raise ImportError
        elif num_residues == 3:
            raise NotImplementedError
        else:
            raise NotImplementedError

        return raw_residue + ((target_index - clue_giver - 1) % self.num_players) * num_residues

    def get_good_actions(self, player_index: int):
        all_other_players_cards = self.get_all_other_players_cards(player_index)
        all_op_unknown_hat_clued_cards = self.get_all_other_players_hat_clued_cards(
            player_index, no_singletons=True
        )
        hand = self.hands[player_index]
        candidates_list = self.all_candidates_list[player_index]

        playable = [
            hand[i].order for i, candidates in enumerate(candidates_list)
            if self.is_playable(candidates)
        ]
        trash = [
            hand[i].order for i, candidates in enumerate(candidates_list)
            if self.is_trash(candidates)
        ]

        yoloable = []
        for i, candidates in enumerate(candidates_list):
            if hand[i].order not in self.hat_clued_card_orders:
                # don't yolo cards we haven't explicitly touched lol
                continue

            if self.is_trash(candidates):
                continue

            unique_candidates = candidates.difference(all_other_players_cards)
            if not len(unique_candidates) or self.is_trash(unique_candidates):
                # this is covered in another type of "good action" below
                continue

            if self.is_playable(unique_candidates.difference(self.trash)):
                yoloable.append(hand[i].order)

        dupe_in_own_hand = []
        dupe_in_other_hand = []
        dupe_in_other_hand_or_trash = []
        seen_in_other_hand = []

        fully_knowns = self.get_fully_known_card_orders(player_index)
        for (suit_index, rank), orders in fully_knowns.items():
            if len(orders) > 1:
                dupe_in_own_hand += orders[1:]

        for i, candidates in enumerate(candidates_list):
            # only count unknown hat clued cards for the purposes of determining "dupedness"
            if not len(candidates.difference(all_op_unknown_hat_clued_cards)):
                dupe_in_other_hand.append(hand[i].order)
            elif not len(candidates.difference(all_op_unknown_hat_clued_cards.union(self.trash))):
                dupe_in_other_hand_or_trash.append(hand[i].order)
            elif not len(candidates.difference(all_other_players_cards)):
                seen_in_other_hand.append(hand[i].order)

        return {
            'playable': playable,
            'trash': trash,
            'yoloable': yoloable,
            'dupe_in_own_hand': dupe_in_own_hand,
            'dupe_in_other_hand': dupe_in_other_hand,
            'dupe_in_other_hand_or_trash': dupe_in_other_hand_or_trash,
            'seen_in_other_hand': seen_in_other_hand
        }

    def write_note(self, order: int, note: str, candidates=None, append=True):
        _note = "t" + str(self.turn + 1) + ": "
        if candidates is not None:
            suit_names = SUITS[self.variant_name]
            if not self.is_trash(candidates):
                _note += "[" + ",".join([
                    suit_names[suit_index] + " " + str(rank) for (suit_index, rank) in candidates
                ]) + "]"
            else:
                _note += "[trash]"
        _note += note

        if order not in self.notes:
            self.notes[order] = _note
            return

        existing_note = self.notes[order]
        if append:
            self.notes[order] += (" | " + _note)
        else:
            self.notes[order] = _note


def test_get_num_available_color_clues():
    assert get_available_color_clues('No Variant') == ["Red", "Yellow", "Green", "Blue", "Purple"]
    assert get_available_color_clues('6 Suits') == ["Red", "Yellow", "Green", "Blue", "Purple", "Teal"]
    assert get_available_color_clues('Black (6 Suits)') == ["Red", "Yellow", "Green", "Blue", "Purple", "Black"]
    assert get_available_color_clues('Pink (6 Suits)') == ["Red", "Yellow", "Green", "Blue", "Purple", "Pink"]
    assert get_available_color_clues('Brown (6 Suits)') == ["Red", "Yellow", "Green", "Blue", "Purple", "Brown"]
    assert get_available_color_clues('Pink & Brown (6 Suits)') == ["Red", "Yellow", "Green", "Blue", "Pink", "Brown"]
    assert get_available_color_clues('Black & Pink (5 Suits)') == ["Red", "Green", "Blue", "Black", "Pink"]
    assert get_available_color_clues('Omni (5 Suits)') == ["Red", "Yellow", "Green", "Blue"]
    assert get_available_color_clues('Rainbow & Omni (5 Suits)') == ["Red", "Green", "Blue"]
    assert get_available_color_clues('Rainbow & White (4 Suits)') == ["Red", "Blue"]
    assert get_available_color_clues("Null & Muddy Rainbow (4 Suits)") == ["Red", "Blue"]
    assert get_available_color_clues("Null & Muddy Rainbow (4 Suits)") == ["Red", "Blue"]
    assert get_available_color_clues("White & Null (3 Suits)") == ["Red"]
    assert get_available_color_clues("Omni & Muddy Rainbow (3 Suits)") == ["Red"]
    
def test_get_all_touched_cards():
    assert get_all_touched_cards(COLOR_CLUE, 1, "No Variant") == {(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)}
    assert get_all_touched_cards(RANK_CLUE, 2, "No Variant") == {(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 2, "Rainbow (4 Suits)") == {
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Rainbow (4 Suits)") == {(0, 2), (1, 2), (2, 2), (3, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 3, "Pink (4 Suits)") == {(3, 1), (3, 2), (3, 3), (3, 4), (3, 5)}
    assert get_all_touched_cards(RANK_CLUE, 2, "Pink (4 Suits)") == {
        (0, 2), (1, 2), (2, 2), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "White (4 Suits)") == {(2, 1), (2, 2), (2, 3), (2, 4), (2, 5)}
    assert get_all_touched_cards(RANK_CLUE, 2, "White (4 Suits)") == {(0, 2), (1, 2), (2, 2), (3, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 3, "Brown (4 Suits)") == {(3, 1), (3, 2), (3, 3), (3, 4), (3, 5)}
    assert get_all_touched_cards(RANK_CLUE, 2, "Brown (4 Suits)") == {(0, 2), (1, 2), (2, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 2, "Muddy Rainbow (4 Suits)") == {
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Muddy Rainbow (4 Suits)") == {(0, 2), (1, 2), (2, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 2, "Light Pink (4 Suits)") == {(2, 1), (2, 2), (2, 3), (2, 4), (2, 5)}
    assert get_all_touched_cards(RANK_CLUE, 2, "Light Pink (4 Suits)") == {
        (0, 2), (1, 2), (2, 2), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Omni (4 Suits)") == {
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Omni (4 Suits)") == {
        (0, 2), (1, 2), (2, 2), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Null (4 Suits)") == {(2, 1), (2, 2), (2, 3), (2, 4), (2, 5)}
    assert get_all_touched_cards(RANK_CLUE, 2, "Null (4 Suits)") == {(0, 2), (1, 2), (2, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 1, "Rainbow & Omni (4 Suits)") == {
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Rainbow & Omni (4 Suits)") == {
        (0, 2), (1, 2), (2, 2), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Dark Rainbow (5 Suits)") == {
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Pink (5 Suits)") == {
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Brown (5 Suits)") == {(0, 2), (1, 2), (2, 2), (3, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 2, "Cocoa Rainbow (5 Suits)") == {
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Cocoa Rainbow (5 Suits)") == {(0, 2), (1, 2), (2, 2), (3, 2)}
    assert get_all_touched_cards(RANK_CLUE, 2, "Gray Pink (5 Suits)") == {
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Dark Omni (5 Suits)") == {
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Omni (5 Suits)") == {
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)
    }
    assert get_all_touched_cards(RANK_CLUE, 2, "Dark Null (5 Suits)") == {(0, 2), (1, 2), (2, 2), (3, 2)}
    assert get_all_touched_cards(COLOR_CLUE, 0, "Null & Prism (5 Suits)") == {
        (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (4, 1), (4, 4)
    }
    assert get_all_touched_cards(COLOR_CLUE, 1, "Null & Prism (5 Suits)") == {
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (4, 2), (4, 5)
    }
    assert get_all_touched_cards(COLOR_CLUE, 2, "Null & Prism (5 Suits)") == {
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (4, 3)
    }

def test_game_state_playables_criticals():
    state = GameState()
    state.set_variant_name("Black (6 Suits)")
    state.stacks[2] += 1
    state.stacks[5] += 2
    state.discards = {(2, 1): 2, (2, 4): 1, (1, 2): 1, (3, 1): 2}
    assert sorted(state.playables) == [(0, 1), (1, 1), (2, 2), (3, 1), (4, 1), (5, 3)]
    assert sorted(state.criticals) == [
        (0, 5), (1, 2), (1, 5), (2, 4), (2, 5), (3, 1), (3, 5), (4, 5), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5)
    ]


if __name__ == "__main__":
    np.random.seed(20000)
    variant_name = "Prism (5 Suits)"
    player_names = ['test0', 'test1', 'test2', 'test3']
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
                    states[player_iterate].handle_draw(player_index, order, card.suit_index, card.rank)
            order += 1

    state = states['test0']
    state.stacks = [0, 2, 0, 0, 0]
    state.discards[(0,1)] = 2
    state.discards[(4,1)] = 2
    state.all_candidates_list[state.our_player_index][3] = {(0,1),(3,1),(4,1)}
    state.all_candidates_list[state.our_player_index][2] = {(4,1),(0,1)}
    state.all_candidates_list[state.our_player_index][1] = {(4,1),(3,1),(0,1)}
    state.all_candidates_list[state.our_player_index][0] = {(4,1),(4,5),(3,1)}
    state.process_visible_cards()

    #state.handle_clue(clue_giver=3, target_index=0, clue_type=COLOR_CLUE, clue_value=3, card_orders=[3, 1])
    #state.handle_clue(clue_giver=3, target_index=0, clue_type=RANK_CLUE, clue_value=3, card_orders=[3, 1])
    #a = state.get_hat_residue(clue_giver=2, target_index=0, clue_type=RANK_CLUE, clue_value=2, card_orders=[0])

    state.print()
    print(state.get_legal_hat_clues())
    #print(a)
    2/0

    test_get_num_available_color_clues()
    test_get_all_touched_cards()
    test_game_state_playables_criticals()
