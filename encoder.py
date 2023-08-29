from game_state import (
    Card,
    GameState,
    SUITS,
    get_all_cards,
    RANK_CLUE,
    COLOR_CLUE,
    is_brownish_pinkish,
    is_whiteish_rainbowy,
    get_all_touched_cards,
    get_available_color_clues,
    get_available_rank_clues
)

from typing import Dict, List, Set, Optional, Tuple


def get_playful_mod_table(variant_name: str, preferred_modulus=None):
    # trash is marked as (0, 0)
    # playable is marked as (-1, 0)
    # stack x + n is marked as (x, -n)
    num_suits = len(SUITS[variant_name])
    all_cards = get_all_cards(variant_name)
    if num_suits == 6:
        if preferred_modulus == 12:
            mod_table = {
                False: {
                    0: [(0, 0)],
                    1: [(-1, 0)],
                    2: [(0, -2), (3, -2)],
                    3: [(1, -2)],
                    4: [(2, -2)],
                    5: [(4, -2)],
                    6: [(5, -2)],
                    7: [(0, -3), (3, -3)],
                    8: [(1, -3), (4, -3)],
                    9: [(2, -3), (5, -3)],
                    10: [(0, -4), (1, -5), (2, -4), (3, -5), (4, -4), (5, -5)],
                    11: [(0, -5), (1, -4), (2, -5), (3, -4), (4, -5), (5, -4)],
                },
                True: {
                    0: [(0, 0)],
                    1: [(-1, 0)],
                    2: [(0, -2)],
                    3: [(1, -2)],
                    4: [(2, -2)],
                    5: [(3, -2)],
                    6: [(4, -2)],
                    7: [(5, -2)],
                    8: [(0, -3), (3, -3)],
                    9: [(1, -3), (4, -3)],
                    10: [(2, -3), (5, -3)],
                    11: [
                        (0, -4),
                        (1, -4),
                        (2, -4),
                        (3, -4),
                        (4, -4),
                        (5, -4),
                        (0, -5),
                        (1, -5),
                        (2, -5),
                        (3, -5),
                        (4, -5),
                        (5, -5),
                    ],
                },
            }
        elif preferred_modulus == 16:
            mod_table = {
                False: {
                    0: [(0, 0)],
                    1: [(0, -1), (2, -1), (4, -1)],
                    2: [(1, -1), (3, -1), (5, -1)],
                    3: [(0, -2)],
                    4: [(1, -2)],
                    5: [(2, -2)],
                    6: [(3, -2)],
                    7: [(4, -2)],
                    8: [(5, -2)],
                    9: [(0, -3), (3, -3)],
                    10: [(1, -3), (4, -3)],
                    11: [(2, -3), (5, -3)],
                    12: [(0, -4), (1, -5), (2, -4)],
                    13: [(3, -4), (4, -5), (5, -4)],
                    14: [(1, -4), (3, -5), (5, -5)],
                    15: [(0, -5), (2, -5), (4, -4)],
                },
                True: {
                    0: [(0, 0)],
                    1: [(0, -1), (2, -1), (4, -1)],
                    2: [(1, -1), (3, -1), (5, -1)],
                    3: [(0, -2)],
                    4: [(1, -2)],
                    5: [(2, -2)],
                    6: [(3, -2)],
                    7: [(4, -2)],
                    8: [(5, -2)],
                    9: [(0, -3), (3, -3)],
                    10: [(1, -3)],
                    11: [(2, -3)],
                    12: [(4, -3)],
                    13: [(5, -3)],
                    14: [(0, -4), (1, -5), (2, -4), (3, -5), (4, -4), (5, -5)],
                    15: [(0, -5), (1, -4), (2, -5), (3, -4), (4, -5), (5, -4)],
                },
            }
    elif num_suits == 5:
        if preferred_modulus == 12:
            mod_table = {
                False: {
                    0: [(0, 0)],
                    1: [(-1, 0)],
                    2: [(0, -2)],
                    3: [(1, -2)],
                    4: [(2, -2)],
                    5: [(3, -2)],
                    6: [(4, -2)],
                    7: [(0, -3), (2, -3)],
                    8: [(1, -3), (3, -3)],
                    9: [(4, -3)],
                    10: [(0, -4), (1, -5), (2, -4), (3, -5), (4, -4)],
                    11: [(0, -5), (1, -4), (2, -5), (3, -4), (4, -5)],
                },
                True: {
                    0: [(0, 0)],
                    1: [(-1, 0)],
                    2: [(0, -2)],
                    3: [(1, -2)],
                    4: [(2, -2)],
                    5: [(3, -2)],
                    6: [(4, -2)],
                    7: [(0, -3), (2, -3)],
                    8: [(1, -3), (3, -3)],
                    9: [(4, -3)],
                    10: [(0, -4), (1, -5), (2, -4), (3, -5), (4, -4)],
                    11: [(0, -5), (1, -4), (2, -5), (3, -4), (4, -5)],
                },
            }
        elif preferred_modulus == 16:
            mod_table = {
                False: {
                    0: [(0, 0)],
                    1: [(0, -1), (1, -1)],
                    2: [(2, -1), (3, -1)],
                    3: [(4, -1)],
                    4: [(0, -2)],
                    5: [(1, -2)],
                    6: [(2, -2)],
                    7: [(3, -2)],
                    8: [(4, -2)],
                    9: [(0, -3)],
                    10: [(1, -3)],
                    11: [(2, -3)],
                    12: [(3, -3)],
                    13: [(4, -3)],
                    14: [(0, -4), (1, -5), (2, -4), (3, -5), (4, -4)],
                    15: [(0, -5), (1, -4), (2, -5), (3, -4), (4, -5)],
                },
                True: {
                    0: [(0, 0)],
                    1: [(0, -1), (1, -1)],
                    2: [(2, -1), (3, -1)],
                    3: [(4, -1)],
                    4: [(0, -2)],
                    5: [(1, -2)],
                    6: [(2, -2)],
                    7: [(3, -2)],
                    8: [(4, -2)],
                    9: [(0, -3)],
                    10: [(1, -3)],
                    11: [(2, -3)],
                    12: [(3, -3)],
                    13: [(4, -3)],
                    14: [(0, -4), (1, -5), (2, -4), (3, -5), (4, -4)],
                    15: [(0, -5), (1, -4), (2, -5), (3, -4), (4, -5)],
                },
            }
        elif preferred_modulus == 20:
            mod_table = {
                False: {
                    0: [(0, 0)],
                    1: [(0, -1), (2, -1)],
                    2: [(1, -1)],
                    3: [(3, -1)],
                    4: [(4, -1)],
                    5: [(0, -2)],
                    6: [(1, -2)],
                    7: [(2, -2)],
                    8: [(3, -2)],
                    9: [(4, -2)],
                    10: [(0, -3)],
                    11: [(1, -3)],
                    12: [(2, -3)],
                    13: [(3, -3)],
                    14: [(4, -3)],
                    15: [(0, -4), (3, -5)],
                    16: [(1, -4), (4, -5)],
                    17: [(2, -4), (0, -5)],
                    18: [(3, -4), (1, -5)],
                    19: [(4, -4), (2, -5)],
                },
                True: {
                    0: [(0, 0)],
                    1: [(0, -1), (2, -1)],
                    2: [(1, -1)],
                    3: [(3, -1)],
                    4: [(4, -1)],
                    5: [(0, -2)],
                    6: [(1, -2)],
                    7: [(2, -2)],
                    8: [(3, -2)],
                    9: [(4, -2)],
                    10: [(0, -3)],
                    11: [(1, -3)],
                    12: [(2, -3)],
                    13: [(3, -3)],
                    14: [(4, -3)],
                    15: [(0, -4), (3, -5)],
                    16: [(1, -4), (4, -5)],
                    17: [(2, -4), (0, -5)],
                    18: [(3, -4), (1, -5)],
                    19: [(4, -4), (2, -5)],
                },
            }
    elif num_suits == 4:
        if preferred_modulus == 12:
            mod_table = {
                False: {
                    0: [(0, 0)],
                    1: [(0, -1), (2, -1)],
                    2: [(1, -1), (3, -1)],
                    3: [(0, -2)],
                    4: [(1, -2)],
                    5: [(2, -2)],
                    6: [(3, -2)],
                    7: [(0, -3), (2, -3)],
                    8: [(1, -3), (3, -3)],
                    9: [(0, -4), (2, -5)],
                    10: [(1, -4), (3, -5)],
                    11: [(0, -5), (1, -5), (2, -4), (3, -4)],
                },
                True: {
                    0: [(0, 0)],
                    1: [(0, -1), (2, -1)],
                    2: [(1, -1), (3, -1)],
                    3: [(0, -2)],
                    4: [(1, -2)],
                    5: [(2, -2)],
                    6: [(3, -2)],
                    7: [(0, -3), (2, -3)],
                    8: [(1, -3), (3, -3)],
                    9: [(0, -4), (2, -5)],
                    10: [(1, -4), (3, -5)],
                    11: [(0, -5), (1, -5), (2, -4), (3, -4)],
                },
            }
        elif preferred_modulus == 16:
            mod_table = {
                False: {
                    0: [(0, 0)],
                    1: [(0, -1)],
                    2: [(1, -1)],
                    3: [(2, -1)],
                    4: [(3, -1)],
                    5: [(0, -2)],
                    6: [(1, -2)],
                    7: [(2, -2)],
                    8: [(3, -2)],
                    9: [(0, -3)],
                    10: [(1, -3)],
                    11: [(2, -3)],
                    12: [(3, -3)],
                    13: [(0, -4), (1, -5)],
                    14: [(1, -4), (2, -5), (3, -4)],
                    15: [(0, -5), (2, -4), (3, -5)],
                },
                True: {
                    0: [(0, 0)],
                    1: [(0, -1)],
                    2: [(1, -1)],
                    3: [(2, -1)],
                    4: [(3, -1)],
                    5: [(0, -2)],
                    6: [(1, -2)],
                    7: [(2, -2)],
                    8: [(3, -2)],
                    9: [(0, -3)],
                    10: [(1, -3)],
                    11: [(2, -3)],
                    12: [(3, -3)],
                    13: [(0, -4), (1, -5)],
                    14: [(1, -4), (2, -5), (3, -4)],
                    15: [(0, -5), (2, -4), (3, -5)],
                },
            }
    return mod_table


class EncoderGameState(GameState):
    def __init__(self, variant_name, player_names, our_player_index):
        super().__init__(variant_name, player_names, our_player_index)
        self.other_info_clued_card_orders["hat_clued_card_orders"] = set()

    @property
    def hat_clued_card_orders(self) -> Set[int]:
        return self.other_info_clued_card_orders["hat_clued_card_orders"]

    def set_variant_name(self, variant_name: str, num_players: int):
        super().set_variant_name(variant_name, num_players)
        if num_players == 4:
            self.mod_table = get_playful_mod_table(variant_name, preferred_modulus=12)
        elif num_players == 5:
            self.mod_table = get_playful_mod_table(variant_name, preferred_modulus=16)
        elif num_players == 6:
            self.mod_table = get_playful_mod_table(variant_name, preferred_modulus=20)
        else:
            raise NotImplementedError

    def get_rightmost_unnumbered_card(self, player_index) -> Optional[Card]:
        for card in self.hands[player_index]:  # iterating oldest to newest
            if card.order not in self.rank_clued_card_orders:
                return card
        return None

    def get_rightmost_uncolored_card(self, player_index) -> Optional[Card]:
        for card in self.hands[player_index]:  # iterating oldest to newest
            if card.order not in self.color_clued_card_orders:
                return card
        return None

    def get_leftmost_non_hat_clued_card(self, player_index) -> Optional[Card]:
        for j in range(len(self.hands[player_index])):
            card = self.hands[player_index][-j - 1]
            if card.order not in self.hat_clued_card_orders:
                return card
        return None

    def get_all_other_players_hat_clued_cards(
        self, player_index=None, no_singletons=False
    ) -> Set[Tuple[int, int]]:
        if no_singletons:
            return {
                (c.suit_index, c.rank)
                for pindex, hand in self.hands.items()
                for i, c in enumerate(hand)
                if pindex not in {self.our_player_index, player_index}
                and c.order in self.hat_clued_card_orders
                and len(self.all_candidates_list[pindex][i]) > 1
            }
        else:
            return {
                (c.suit_index, c.rank)
                for pindex, hand in self.hands.items()
                for c in hand
                if pindex not in {self.our_player_index, player_index}
                and c.order in self.hat_clued_card_orders
            }

    def get_leftmost_non_hat_clued_cards(self):
        result = []
        for player_index, hand in self.hands.items():
            if player_index == self.our_player_index:
                continue
            lnhc = self.get_leftmost_non_hat_clued_card(player_index)
            result.append(lnhc)
        return result

    @property
    def mod_base(self) -> int:
        return max(self.mod_table[False]) + 1

    @property
    def num_residues_per_player(self) -> int:
        return int(self.mod_base / (self.num_players - 1))

    @property
    def identity_to_residue(self) -> Dict[Tuple[int, int], int]:
        result = {}
        trash_residue = 0
        most_1s_played = self.num_1s_played > len(SUITS[self.variant_name]) / 2.0

        for residue, identities in self.mod_table[most_1s_played].items():
            # trash is marked as (0, 0)
            # playable is marked as (-1, 0)
            # stack x + n is marked as (x, -n)
            for identity in identities:
                if identity == (-1, 0):
                    for playable in self.playables:
                        result[playable] = residue
                elif identity[1] < 0:
                    # blue stack is 2, identity of (3, -2) is blue 4
                    rank = self.stacks[identity[0]] - identity[1]
                    result[(identity[0], rank)] = residue
                elif identity == (0, 0):
                    trash_residue = residue

        # override explicit identities
        for residue, identities in self.mod_table[most_1s_played].items():
            for identity in identities:
                if identity[1] > 0:
                    result[identity] = residue

        # override trash
        for suit_index, rank in self.trash:
            result[(suit_index, rank)] = trash_residue

        return result

    @property
    def residue_to_identities(self) -> Dict[int, Set[Tuple[int, int]]]:
        result = {}
        for identity, residue in self.identity_to_residue.items():
            if residue not in result:
                result[residue] = set()
            result[residue].add(identity)
        return result

    def handle_clue(
        self,
        clue_giver: int,
        target_index: int,
        clue_type: int,
        clue_value: int,
        card_orders,
    ):
        order_to_index = self.order_to_index
        identity_to_residue = self.identity_to_residue
        residue_to_identities = self.residue_to_identities
        hat_residue = self.get_hat_residue(
            clue_giver, target_index, clue_type, clue_value, card_orders
        )

        sum_of_others_residues = 0
        for player_index, hand in self.hands.items():
            if player_index in {self.our_player_index, clue_giver}:
                continue

            left_non_hat_clued = self.get_leftmost_non_hat_clued_card(player_index)
            if left_non_hat_clued is None:
                continue

            other_residue = identity_to_residue[
                (left_non_hat_clued.suit_index, left_non_hat_clued.rank)
            ]
            print(
                self.player_names[player_index]
                + " "
                + str(left_non_hat_clued)
                + " has residue "
                + str(other_residue)
            )
            sum_of_others_residues += other_residue

            _, i = order_to_index[left_non_hat_clued.order]
            new_candidates = self.all_candidates_list[player_index][i].intersection(
                residue_to_identities[other_residue]
            )
            if len(new_candidates):
                self.all_candidates_list[player_index][i] = new_candidates

                self.write_note(
                    left_non_hat_clued.order, note="", candidates=new_candidates
                )
                self.hat_clued_card_orders.add(left_non_hat_clued.order)
            else:
                self.write_note(
                    left_non_hat_clued.order,
                    note="someone messed up and gave a bad hat clue",
                )

        if self.our_player_index != clue_giver:
            my_residue = (hat_residue - sum_of_others_residues) % self.mod_base
            print(f"My ({self.our_player_name})) residue = {my_residue}.")
            print(f"Hat candidates: {residue_to_identities[my_residue]}")
            left_non_hat_clued = self.get_leftmost_non_hat_clued_card(
                self.our_player_index
            )
            if left_non_hat_clued is not None:
                _, i = order_to_index[left_non_hat_clued.order]
                new_candidates = self.all_candidates_list[self.our_player_index][
                    i
                ].intersection(residue_to_identities[my_residue])
                self.all_candidates_list[self.our_player_index][i] = new_candidates
                self.write_note(
                    left_non_hat_clued.order, note="", candidates=new_candidates
                )
                self.hat_clued_card_orders.add(left_non_hat_clued.order)

        return super().handle_clue(
            clue_giver, target_index, clue_type, clue_value, card_orders
        )

    def get_special_hat_clues(
        self, variant_name: str, target_index: int, clue_mapping_only=False
    ) -> Dict:
        all_3color_wr_vars = [
            var
            for var in SUITS
            if len(get_available_color_clues(var)) == 3 and is_whiteish_rainbowy(var)
        ]
        base_dct = {
            var: {
                0: [(RANK_CLUE, 5), (RANK_CLUE, 1)],
                1: [(COLOR_CLUE, 0), (RANK_CLUE, 2)],
                2: [(COLOR_CLUE, 1), (RANK_CLUE, 3)],
                3: [(COLOR_CLUE, 2), (RANK_CLUE, 4)],
            }
            for var in all_3color_wr_vars
        }

        base_dct["Valentine Mix (6 Suits)"] = {
            0: [(RANK_CLUE, 5), (RANK_CLUE, 1)],
            1: [(RANK_CLUE, 2), (COLOR_CLUE, 0)],
            2: [(COLOR_CLUE, 1), (RANK_CLUE, 3)],
            3: [(RANK_CLUE, 4)],
        }
        base_dct["Valentine Mix (5 Suits)"] = {
            0: [(RANK_CLUE, 5), (RANK_CLUE, 1)],
            1: [(RANK_CLUE, 2), (COLOR_CLUE, 0)],
            2: [(COLOR_CLUE, 1), (RANK_CLUE, 3)],
            3: [(RANK_CLUE, 4)],
        }

        dct = base_dct.get(variant_name, {})

        if clue_mapping_only:
            return dct if len(dct) else None

        return (
            {
                raw_residue: self.get_cards_touched_dict(target_index, clue_type_values)
                for raw_residue, clue_type_values in dct.items()
            }
            if len(dct)
            else None
        )

    def get_legal_clues(self) -> Dict[Tuple[int, int, int], Set[Tuple[int, int]]]:
        # (clue_value, clue_type, target_index) -> cards_touched
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
        target_index = (
            self.our_player_index + 1 + (sum_of_residues // num_residues)
        ) % self.num_players
        raw_residue = sum_of_residues % num_residues
        target_hand = self.hands[target_index]

        assert target_index != self.our_player_index
        print(
            "Evaluating legal hat clues - sum of residues =",
            sum_of_residues,
            "target_index",
            target_index,
        )
        maybe_special_hat_clues = self.get_special_hat_clues(
            self.variant_name, target_index
        )
        if maybe_special_hat_clues is not None:
            return maybe_special_hat_clues[raw_residue]

        if num_residues == 4:
            if raw_residue in {0, 1}:
                if is_brownish_pinkish(self.variant_name):
                    if raw_residue == 0:
                        return self.get_cards_touched_dict(
                            target_index,
                            [(RANK_CLUE, 1), (RANK_CLUE, 3), (RANK_CLUE, 5)],
                        )
                    else:
                        return self.get_cards_touched_dict(
                            target_index,
                            [(RANK_CLUE, 2), (RANK_CLUE, 4)],
                        )
                else:
                    rightmost_unnumbered = self.get_rightmost_unnumbered_card(
                        target_index
                    )
                    # iterate over rank clues
                    # TODO: special 1s/5s
                    rank_to_cards_touched = {}
                    for clue_value in range(1, 6):
                        cards_touched = get_all_touched_cards(
                            RANK_CLUE, clue_value, self.variant_name
                        )
                        cards_touched_in_target_hand = [
                            card
                            for card in target_hand
                            if (card.suit_index, card.rank) in cards_touched
                        ]
                        if len(cards_touched_in_target_hand):
                            rank_to_cards_touched[
                                clue_value
                            ] = cards_touched_in_target_hand

                    if rightmost_unnumbered is None:
                        clue_rank = (
                            min(rank_to_cards_touched)
                            if raw_residue == 0
                            else max(rank_to_cards_touched)
                        )
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
                    if num_colors in {2, 4, 5, 6}:
                        color_to_cards_touched = {}
                        clue_values = (
                            range(num_colors // 2)
                            if raw_residue == 2
                            else range(num_colors // 2, num_colors)
                        )
                        for clue_value in clue_values:
                            cards_touched = get_all_touched_cards(
                                COLOR_CLUE, clue_value, self.variant_name
                            )
                            cards_touched_in_target_hand = [
                                card
                                for card in target_hand
                                if (card.suit_index, card.rank) in cards_touched
                            ]
                            if len(cards_touched_in_target_hand):
                                color_to_cards_touched[
                                    clue_value
                                ] = cards_touched_in_target_hand

                        return {
                            (clue_value, COLOR_CLUE, target_index): cards_touched
                            for clue_value, cards_touched in color_to_cards_touched.items()
                        }
                    else:
                        raise NotImplementedError
                else:
                    rightmost_uncolored = self.get_rightmost_uncolored_card(
                        target_index
                    )
                    # iterate over color clues
                    color_to_cards_touched = {}
                    for clue_value, _ in enumerate(
                        get_available_color_clues(self.variant_name)
                    ):
                        cards_touched = get_all_touched_cards(
                            COLOR_CLUE, clue_value, self.variant_name
                        )
                        cards_touched_in_target_hand = [
                            card
                            for card in target_hand
                            if (card.suit_index, card.rank) in cards_touched
                        ]
                        if len(cards_touched_in_target_hand):
                            color_to_cards_touched[
                                clue_value
                            ] = cards_touched_in_target_hand

                    if rightmost_uncolored is None:
                        clue_color = (
                            min(color_to_cards_touched)
                            if raw_residue == 2
                            else max(color_to_cards_touched)
                        )
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

    def evaluate_clue_score(self, clue_value, clue_type, target_index) -> int:
        all_cards_touched_by_clue = get_all_touched_cards(
            clue_type, clue_value, self.variant_name
        )
        good_card_indices = [
            i
            for i in range(len(self.hands[target_index]))
            if not self.is_trash_card(self.hands[target_index][i])
        ]
        candidates_list = self.all_candidates_list[target_index]
        score = 1

        for i in good_card_indices:
            if self.hands[target_index][i].to_tuple() in all_cards_touched_by_clue:
                new_candidates = candidates_list[i].intersection(
                    all_cards_touched_by_clue
                )
            else:
                new_candidates = candidates_list[i].difference(
                    all_cards_touched_by_clue
                )
            score *= len(new_candidates)

        return -score

    def get_hat_residue(
        self,
        clue_giver: int,
        target_index: int,
        clue_type: int,
        clue_value: int,
        card_orders,
    ):
        # TODO: depends on variant
        num_residues = self.num_residues_per_player
        rightmost_unnumbered = self.get_rightmost_unnumbered_card(target_index)
        rightmost_uncolored = self.get_rightmost_uncolored_card(target_index)

        clue_mappings = self.get_special_hat_clues(
            self.variant_name, target_index, clue_mapping_only=True
        )
        if clue_mappings is not None:
            for raw_residue, clue_type_values in clue_mappings.items():
                for _type, _value in clue_type_values:
                    if clue_type == _type and clue_value == _value:
                        return (
                            raw_residue
                            + ((target_index - clue_giver - 1) % self.num_players)
                            * num_residues
                        )

        if num_residues == 4:
            if clue_type == RANK_CLUE:
                if is_brownish_pinkish(self.variant_name):
                    raw_residue = 0 if clue_value in {1, 3, 5} else 1
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
                    if num_colors in {2, 4, 5, 6}:
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

        return (
            raw_residue
            + ((target_index - clue_giver - 1) % self.num_players) * num_residues
        )

    def get_good_actions(self, player_index: int) -> Dict[str, List[int]]:
        all_other_players_cards = self.get_all_other_players_cards(player_index)
        all_op_unknown_hat_clued_cards = self.get_all_other_players_hat_clued_cards(
            player_index, no_singletons=True
        )
        hand = self.hands[player_index]
        candidates_list = self.all_candidates_list[player_index]

        playable = [
            hand[i].order
            for i, candidates in enumerate(candidates_list)
            if self.is_playable(candidates)
        ]
        trash = [
            hand[i].order
            for i, candidates in enumerate(candidates_list)
            if self.is_trash(candidates)
        ]
        yoloable = []
        for i, candidates in enumerate(candidates_list):
            if hand[i].order not in self.hat_clued_card_orders:
                # don't yolo cards we haven't explicitly touched lol
                continue

            if self.is_trash(candidates):
                continue

            if self.is_playable(candidates.difference(self.trash)):
                yoloable.append(hand[i].order)

        dupe_in_own_hand = []
        dupe_in_other_hand = []
        dupe_in_other_hand_or_trash = []
        seen_in_other_hand = []

        fully_knowns = self.get_fully_known_card_orders(player_index)
        for _, orders in fully_knowns.items():
            if len(orders) > 1:
                dupe_in_own_hand += orders[1:]

        for i, candidates in enumerate(candidates_list):
            # only count unknown hat clued cards for the purposes of determining "dupedness"
            if not len(candidates.difference(all_op_unknown_hat_clued_cards)):
                dupe_in_other_hand.append(hand[i].order)
            elif not len(
                candidates.difference(all_op_unknown_hat_clued_cards.union(self.trash))
            ):
                dupe_in_other_hand_or_trash.append(hand[i].order)
            elif not len(candidates.difference(all_other_players_cards)):
                seen_in_other_hand.append(hand[i].order)

        return {
            "playable": playable,
            "trash": trash,
            "yoloable": yoloable,
            "dupe_in_own_hand": dupe_in_own_hand,
            "dupe_in_other_hand": dupe_in_other_hand,
            "dupe_in_other_hand_or_trash": dupe_in_other_hand_or_trash,
            "seen_in_other_hand": seen_in_other_hand,
        }
