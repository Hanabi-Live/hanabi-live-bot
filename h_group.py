from game_state import GameState, get_all_touched_cards, RANK_CLUE, COLOR_CLUE, Card
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from copy import deepcopy


class BadPlay(Exception):
    pass


class SimulationState:
    def __init__(self, pointer, stacks):
        self.pointer: Tuple[int, int] = pointer
        self.simulation_stacks: List[int] = deepcopy(stacks)
        self.already_played_orders: Set[int] = set()
        self.has_been_incremented: bool = False
        self.additional_cards_gotten: Set[int] = set()

    def increment_pointer(self):
        self.pointer = (self.pointer[0], self.pointer[1] + 1)

    def is_playable(self, card: Card):
        return self.simulation_stacks[card.suit_index] == card.rank - 1

    def play(self, card: Card, finesse: bool = False):
        if not self.is_playable(card):
            raise BadPlay
        self.simulation_stacks[card.suit_index] += 1
        self.already_played_orders.add(card.order)
        if (card.suit_index, card.rank) == self.pointer:
            self.increment_pointer()
            self.has_been_incremented = True

        if finesse:
            self.additional_cards_gotten.add(card.order)


@dataclass
class FinesseNode:
    suit_index: int
    rank: int
    player_index: int
    order_hierarchy: List[int]
    expiry_turn: int
    completed: bool = False

    @property
    def is_valid(self):
        return self.expiry_turn >= 0

    def __str__(self):
        return f"({self.suit_index}, {self.rank}) {self.order_hierarchy[:1]}"

    def __repr__(self):
        return self.__str__()


class FinessePaths:
    def __init__(self, finessed_turn: int):
        self.finessed_turn = finessed_turn
        self.paths: List[Tuple[FinesseNode]] = []

    def add_nodes(self, nodes: List[FinesseNode]):
        self.paths.append(tuple(nodes))

    def update_expiry_turn(
        self, suit_index: int, rank: int, player_index: int, new_turn_num: int
    ):
        for finesse_nodes in self.paths:
            for fn in finesse_nodes:
                if (fn.suit_index, fn.rank, fn.player_index) == (
                    suit_index,
                    rank,
                    player_index,
                ):
                    fn.expiry_turn = new_turn_num

    def print(self):
        for path in self.paths:
            print(" -> ".join([str(x) for x in path]))


class HGroupGameState(GameState):
    def __init__(self, variant_name, player_names, our_player_index):
        super().__init__(variant_name, player_names, our_player_index)
        self.other_info_clued_card_orders["chop_moved_cards"] = set()
        self.order_to_finesse_paths: Dict[int, FinessePaths] = {}

    @property
    def next_player_index(self) -> int:
        return (self.our_player_index + 1) % self.num_players

    @property
    def all_chop_moved_cards(self) -> Set[int]:
        return self.other_info_clued_card_orders["chop_moved_cards"]

    def get_chop_moved_orders(self, player_index: int) -> Set[int]:
        result = set()
        for card in self.hands[player_index]:
            if card.order in self.all_chop_moved_cards:
                result.add(card.order)
        return result

    def get_chop_order(self, player_index: int) -> Optional[int]:
        chop_moved_orders = self.get_chop_moved_orders(player_index)
        for i, card in enumerate(self.hands[player_index]):
            if card.order in chop_moved_orders:
                continue
            if card.order in self.color_clued_card_orders:
                continue
            if card.order in self.rank_clued_card_orders:
                continue
            return card.order
        return None

    def get_focus_of_clue(self, player_index: int, orders_touched: List[int]) -> int:
        chop_order = self.get_chop_order(player_index)
        cards_touched: List[Card] = []
        newly_touched_cards: List[Card] = []
        for card in reversed(self.hands[player_index]):  # iterate left to right
            if card.order not in orders_touched:
                continue

            if card.order == chop_order:
                return chop_order

            cards_touched.append(card)
            if (
                card.order not in self.rank_clued_card_orders
                and card.order in self.color_clued_card_orders
            ):
                newly_touched_cards.append(card)
        if len(newly_touched_cards):
            return newly_touched_cards[0].order
        if len(cards_touched):
            return cards_touched[0].order
        raise ValueError

    def get_good_actions(self, player_index: int) -> Dict[str, List[int]]:
        all_other_players_clued_cards = self.get_all_other_players_clued_cards(
            player_index
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
        dupe_in_own_hand = []
        dupe_in_other_hand = []
        dupe_in_other_hand_or_trash = []
        seen_in_other_hand = []

        fully_knowns = self.get_fully_known_card_orders(player_index)
        for _, orders in fully_knowns.items():
            if len(orders) > 1:
                dupe_in_own_hand += orders[1:]

        for i, candidates in enumerate(candidates_list):
            if not len(candidates.difference(all_other_players_clued_cards)):
                dupe_in_other_hand.append(hand[i].order)
            elif not len(
                candidates.difference(all_other_players_clued_cards.union(self.trash))
            ):
                dupe_in_other_hand_or_trash.append(hand[i].order)
            elif not len(candidates.difference(all_other_players_clued_cards)):
                seen_in_other_hand.append(hand[i].order)

        return {
            "playable": playable,
            "trash": trash,
            "dupe_in_own_hand": dupe_in_own_hand,
            "dupe_in_other_hand": dupe_in_other_hand,
            "dupe_in_other_hand_or_trash": dupe_in_other_hand_or_trash,
            "seen_in_other_hand": seen_in_other_hand,
        }

    def _prompt_others_logic(
        self, target_index: int, sim_state: SimulationState
    ) -> SimulationState:
        if sim_state.has_been_incremented:
            return sim_state

        for player in range(self.num_players):
            if player == target_index or player == self.our_player_index:
                continue

            # only check prompt if the card is in the player's hand to begin with
            all_clued_cards = [
                c.to_tuple() for c in self.hands[player] if self.is_clued(c.order)
            ]
            if sim_state.pointer not in all_clued_cards:
                continue

            for i in range(len(self.all_candidates_list[player])):
                card = self.hands[player][-i - 1]
                if not self.is_clued(card.order):
                    continue

                candidates = self.all_candidates_list[player][-i - 1]
                if sim_state.pointer not in candidates:
                    continue

                identity = self.hands[player][-i - 1].to_tuple()
                if identity == sim_state.pointer:
                    sim_state.play(card)
                    return sim_state

                # raises BadPlay if a bomb occurs
                sim_state.play(card)

        return sim_state

    def _finesse_others_logic(
        self, target_index: int, sim_state: SimulationState
    ) -> SimulationState:
        if sim_state.has_been_incremented:
            return sim_state

        for player in range(self.num_players):
            if player == target_index or player == self.our_player_index:
                continue

            # only check prompt if the card is in the player's hand to begin with
            all_unclued_cards = [
                c.to_tuple() for c in self.hands[player] if not self.is_clued(c.order)
            ]
            if sim_state.pointer not in all_unclued_cards:
                continue

            for i in range(len(self.all_candidates_list[player])):
                card = self.hands[player][-i - 1]
                if self.is_clued(card.order):
                    continue

                candidates = self.all_candidates_list[player][-i - 1]
                if sim_state.pointer not in candidates:
                    continue

                identity = self.hands[player][-i - 1].to_tuple()
                if identity == sim_state.pointer:
                    sim_state.play(card, finesse=True)
                    return sim_state

                # raises BadPlay if a bomb occurs
                sim_state.play(card, finesse=True)

        return sim_state

    def _prompt_self_logic(
        self, target_index: int, target_card: Card, sim_state: SimulationState
    ) -> SimulationState:
        if sim_state.has_been_incremented:
            return sim_state

        all_clued_cards = [
            c.to_tuple() for c in self.hands[target_index] if self.is_clued(c.order)
        ]
        if sim_state.pointer not in all_clued_cards:
            return sim_state

        # ordered from left to right
        all_potential_pointer_clued_cards = []
        for i in range(len(self.all_candidates_list[target_index])):
            card = self.hands[target_index][-i - 1]
            if not self.is_clued(card.order):
                continue

            candidates = self.all_candidates_list[target_index][-i - 1]
            if sim_state.pointer not in candidates:
                continue

            all_potential_pointer_clued_cards.append((i, card.order))

            identity = self.hands[player][-i - 1].to_tuple()
            if identity == sim_state.pointer:
                sim_state.play(card)
                return sim_state

            # raises BadPlay if a bomb occurs
            sim_state.play(card)

        return sim_state

    def get_cards_gotten_from_play_clue(
        self, target_index: int, clue_type: int, clue_value: int
    ) -> Set[int]:
        # does not take into account good touch principle
        # assumes the clue is known to be a play clue, even for e.g. a 2 save
        all_touched = get_all_touched_cards(clue_type, clue_value, self.variant_name)
        orders_touched = [
            c.order
            for c in self.hands[target_index]
            if (c.suit_index, c.rank) in all_touched
        ]
        cards_gotten = set(orders_touched)
        focus_order = self.get_focus_of_clue(target_index, orders_touched)
        order_to_index = self.order_to_index

        _, i = order_to_index[focus_order]
        target_card = self.hands[target_index][i]
        suit_index = target_card.suit_index
        rank = target_card.rank
        if (suit_index, rank) in self.playables:
            return cards_gotten

        # otherwise the card needs some help to play
        # check if card is directly promptable
        missing_cards = [
            (suit_index, i) for i in range(self.stacks[suit_index] + 1, rank)
        ]
        assert len(missing_cards)

        sim_state = SimulationState(missing_cards[0], self.stacks)
        while sim_state.pointer[1] < rank:
            sim_state.has_been_incremented = False
            print(f"Pointer: {sim_state.pointer}")

            try:
                sim_state = self._prompt_others_logic(target_index, deepcopy(sim_state))
            except BadPlay:
                print(f"Got BadPlay attempting to prompt {sim_state.pointer}")
                pass

            try:
                sim_state = self._finesse_others_logic(
                    target_index, deepcopy(sim_state)
                )
            except BadPlay:
                print(f"Got BadPlay attempting to finesse {sim_state.pointer}")
                pass

            # not clued in other's hands - check if clued in own hand
            if False:
                for i in range(len(self.all_candidates_list[player])):
                    order = self.hands[player][-i - 1].order
                    if not self.is_clued(order):
                        continue
                    candidates = self.all_candidates_list[player][-i - 1]
                    if pointer not in candidates:
                        continue

                    identity = self.hands[player][-i - 1].to_tuple()
                    if identity == pointer:
                        print("Incrementing pointer", pointer)
                        pointer = (pointer[0], pointer[1] + 1)
                        simulation_stacks[identity[0]] += 1
                        already_played_orders.add(order)
                        break
                    else:
                        if identity[1] != simulation_stacks[identity[0]] + 1:
                            print("Bombs while prompting")
                            return None  # bombs while prompting
                        else:
                            simulation_stacks[identity[0]] += 1
                            already_played_orders.add(order)

        return cards_gotten.union(sim_state.additional_cards_gotten)

        target_cands_before_clue = self.all_candidates_list[target_index][i]
        target_cands_after_clue = target_cands_before_clue.intersection(all_touched)
        print(focused_card)
        print(target_cands_after_clue)
        2 / 0
        if rank == self.stacks[suit_index] + 1:
            return [candidate]

        for player_index in range(self.num_players):
            pass

        # the play clue doesn't work
        return None

    def handle_clue(
        self,
        clue_giver: int,
        target_index: int,
        clue_type: int,
        clue_value: int,
        card_orders,
    ):
        candidates_list = self.all_candidates_list[target_index]
        focus_order = self.get_focus_of_clue(target_index, card_orders)

        result = super().handle_clue(
            clue_giver, target_index, clue_type, clue_value, card_orders
        )

        return result
        if False:
            finesse_paths = FinessePaths(self.turn)
            _, i = self.order_to_index[focus_order]
            candidates_after_clue = self.all_candidates_list[target_index][i]
            for suit_index, rank in candidates_after_clue:
                nodes: List[FinesseNode] = []
                chain = [
                    (suit_index, i)
                    for i in range(self.stacks[suit_index] + 1, rank + 1)
                ]
                if not len(chain):  # trash card
                    continue

                if len(chain) == 1:
                    s, r = chain[0]
                    finesse_paths.add_nodes(
                        [FinesseNode(s, r, target_index, [focus_order], 9999, True)]
                    )
                else:
                    occupied_orders = set()
                    chain_card_to_player_indices = {}
                    for s, r in chain[:-1]:
                        for player_iterate in range(self.num_players):
                            if player_iterate == clue_giver:
                                continue

                            clued = reversed(self.get_clued_orders(player_iterate))
                            unclued = reversed(self.get_unclued_orders(player_iterate))

                    # raise ZeroDivisionError

            finesse_paths.print()
            2 / 0
        self.order_to_finesse_paths[focus_order] = finesse_paths
        return result
        if False:
            for i, card in enumerate(self.hands[target_index]):
                if card.order == focus_of_clue:
                    if clue_type == RANK_CLUE and clue_value not in {2, 5}:
                        candidates_list[i] = candidates_list[i].intersection(
                            self.playables.union(self.criticals)
                        )
                    elif clue_type == COLOR_CLUE:
                        candidates_list[i] = candidates_list[i].intersection(
                            self.playables.union(self.non_5_criticals)
                        )

    def get_legal_clues(self) -> Dict[Tuple[int, int, int], Set[Tuple[int, int]]]:
        # (clue_value, clue_type, target_index) -> cards_touched
        for target_index in range(self.num_players):
            if target_index == self.our_player_index:
                continue

            # clue_type_values = [(RANK_CLUE, 1), (COLOR_CLUE, 1)]
            # self.get_cards_touched_dict(self, target_index, clue_type_values)


if __name__ == "__main__":
    import numpy as np
    from game_state import get_random_deck

    np.random.seed(20000)
    variant_name = "Prism (5 Suits)"
    player_names = ["test0", "test1", "test2", "test3"]
    states = {
        player_index: GameState(variant_name, player_names, player_index)
        for player_index, player_name in enumerate(player_names)
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

    states[0].print()
