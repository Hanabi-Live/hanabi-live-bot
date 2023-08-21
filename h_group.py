from game_state import GameState, get_all_touched_cards, RANK_CLUE, COLOR_CLUE, Card
from typing import Dict, List, Tuple, Optional, Set

FinessePath = Tuple[Tuple[int, int, int]]


class HGroupGameState(GameState):
    def __init__(self, variant_name, player_names, our_player_index):
        super().__init__(variant_name, player_names, our_player_index)
        self.other_info_clued_card_orders["chop_moved_cards"] = set()
        self.finesse_path_turn_updates: Dict[FinessePath, List[int]] = {}

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

    def get_focus_of_clue(
        self, player_index: int, orders_touched: List[int]
    ) -> Optional[int]:
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
        return None

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

    def handle_clue(
        self,
        clue_giver: int,
        target_index: int,
        clue_type: int,
        clue_value: int,
        card_orders,
    ):
        candidates_list = self.all_candidates_list[target_index]
        focus_of_clue = self.get_focus_of_clue(target_index, card_orders)

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

        return super().handle_clue(
            clue_giver, target_index, clue_type, clue_value, card_orders
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
