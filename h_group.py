from game_state import GameState, get_all_touched_cards, RANK_CLUE, COLOR_CLUE
from typing import Dict, List, Tuple, Optional, Set

FinessePath = Tuple[Tuple[int, int, int]]


class HGroupGameState(GameState):
    def __init__(self, variant_name, player_names, our_player_index):
        super().__init__(variant_name, player_names, our_player_index)
        self.other_info_clued_card_orders["chop_moved_cards"] = set()
        self.finesse_path_turn_updates: Dict[FinessePath, List[int]] = {}

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

    def get_good_actions(self, player_index: int) -> Dict[str, List[int]]:
        return {}

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

        for i, card in enumerate(self.hands[target_index]):
            if card.order in card_orders:
                touched_cards.append(card)
                candidates_list[i] = candidates_list[i].intersection(
                    all_cards_touched_by_clue
                )
            else:
                candidates_list[i] = candidates_list[i].difference(
                    all_cards_touched_by_clue
                )

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
