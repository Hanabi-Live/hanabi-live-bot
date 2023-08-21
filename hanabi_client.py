import json
import websocket

from constants import ACTION, COLOR_CLUE, RANK_CLUE
from game_state import GameState
from encoder import EncoderGameState
from h_group import HGroupGameState
import traceback
from typing import Dict, Type


def is_int(x):
    try:
        int(x)
        return True
    except Exception:
        return False


class HanabiClient:
    def __init__(self, url, cookie, bot_to_join: str, convention: str):
        self.bot_to_join = bot_to_join
        self.convention_name = (
            convention.replace("_", "").replace("-", "").replace(" ", "").lower()
        )
        self.game_state_cls: Type[GameState] = {
            "encoder": EncoderGameState,
            "hgroup": HGroupGameState,
        }[self.convention_name]

        # Initialize all class variables
        self.commandHandlers = {}
        self.tables = {}
        self.username = ""
        self.ws = None
        self.action_time = False
        self.everyone_connected = False
        self.games: Dict[int, GameState] = {}

        # Initialize the website command handlers (for the lobby)
        self.commandHandlers["welcome"] = self.welcome
        self.commandHandlers["warning"] = self.warning
        self.commandHandlers["error"] = self.error
        self.commandHandlers["chat"] = self.chat
        self.commandHandlers["table"] = self.table
        self.commandHandlers["tableList"] = self.table_list
        self.commandHandlers["tableGone"] = self.table_gone
        self.commandHandlers["tableStart"] = self.table_start

        # Initialize the website command handlers (for the game)
        self.commandHandlers["init"] = self.init
        self.commandHandlers["gameAction"] = self.game_action
        self.commandHandlers["gameActionList"] = self.game_action_list
        self.commandHandlers["databaseID"] = self.database_id
        self.commandHandlers["connected"] = self.connected
        self.commandHandlers["clock"] = self.clock
        self.commandHandlers["user"] = self.user
        self.commandHandlers["noteListPlayer"] = self.note_list_player
        self.commandHandlers["chatTyping"] = self.chat_typing

        # Start the WebSocket client
        print(f'Connecting to "{url}".')

        self.ws = websocket.WebSocketApp(
            url,
            on_message=lambda ws, message: self.websocket_message(ws, message),
            on_error=lambda ws, error: self.websocket_error(ws, error),
            on_open=lambda ws: self.websocket_open(ws),
            on_close=lambda ws: self.websocket_close(ws),
            cookie=cookie,
        )
        self.ws.run_forever()

    def websocket_message(self, ws, message):
        # WebSocket messages from the server come in the format of:
        # commandName {"field_name":"value"}
        # For more information, see:
        # https://github.com/Hanabi-Live/hanabi-live/blob/main/server/src/actions.go
        result = message.split(" ", 1)  # Split it into two things
        if len(result) != 1 and len(result) != 2:
            print("error: received an invalid WebSocket message:")
            print(message)
            return

        command = result[0]
        try:
            data = json.loads(result[1])
        except:
            print(f'error: the JSON data for the command of "{command}" was invalid')
            return

        if command in self.commandHandlers:
            if command not in {"gameAction", "clock", "warning", "user"}:
                print('debug: got command "' + command + '"')

            try:
                self.commandHandlers[command](data)
            except Exception as e:
                print("**************************\n" * 3)
                print('error: command handler for "' + command + '" failed, details:\n')
                traceback.print_exc()
                print("**************************\n" * 3)
                return
        else:
            print(f'debug: ignoring command "{command}"')

    def websocket_error(self, ws, error):
        print(f"Encountered a WebSocket error: {error}")

    def websocket_close(self, ws):
        print("WebSocket connection closed.")

    def websocket_open(self, ws):
        print("Successfully established WebSocket connection.")

    # --------------------------------
    # Website Command Handlers (Lobby)
    # --------------------------------

    def welcome(self, data):
        # The "welcome" message is the first message that the server sends us
        # once we have established a connection
        # It contains our username, settings, and so forth
        self.username = data["username"]
        if self.bot_to_join == "create":
            self.chat_create_table()

    def error(self, data):
        # Either we have done something wrong,
        # or something has gone wrong on the server
        print(data)

    def warning(self, data):
        # We have done something wrong
        print(data)

    def chat(self, data):
        # We only care about private messages
        if data["recipient"] != self.username:
            return

        # We only care about private messages that start with a forward slash
        if not data["msg"].startswith("/"):
            return

        args = data["msg"][1:].split(" ")
        command = args[0]

        if command == "join":
            player_name = args[1] if len(args) > 1 else None
            self.chat_join(data, player_name)
        elif command == "create":
            self.chat_create_table()
        elif command == "start":
            self.chat_start()
        elif command in {"setvariant", "set_variant"}:
            variant_name = (
                (
                    args[1]
                    .replace("_", " ")
                    .replace("+", " & ")
                    .replace("6s", "(6 Suits)")
                    .replace("5s", "(5 Suits)")
                    .replace("4s", "(4 Suits)")
                    .replace("3s", "(3 Suits)")
                )
                if len(args) > 1
                else None
            )
            self.chat_set_variant(variant_name)
        elif command == "terminate":
            table_id = args[1] if len(args) > 1 else None
            self.chat_terminate(table_id)
        elif command == "reattend":
            table_id = args[1] if len(args) > 1 else 0
            self.chat_reattend(table_id)
        elif command == "restart":
            self.chat_restart()
        else:
            msg = "That is not a valid command."
            self.chat_reply(msg, data["who"])

    def chat_join(self, data, player_name=None):
        # Someone sent a private message to the bot and requested that we join
        # their game
        # Find the table that the current user is currently in
        table_id = None

        if is_int(player_name):
            self.send("tableJoin", {"tableID": int(player_name)})
            return

        if player_name is None:
            player_name = data.get("who", "")

        print(player_name)
        print("-----------")
        for table in self.tables.values():
            # Ignore games that have already started (and shared replays)
            if table["running"]:
                continue

            if player_name in table["players"]:
                if len(table["players"]) == 6:
                    msg = "Your game is full. Please make room for me before requesting that I join your game."
                    self.chat_reply(msg, data["who"])
                    return

                table_id = table["id"]
                break

        if table_id is None:
            msg = "Please create a table first before requesting that I join your game."
            self.chat_reply(msg, data["who"])
            return

        self.send("tableJoin", {"tableID": table_id})

    def chat_reattend(self, table_id: int):
        self.send("reattend", {"tableID": table_id})

    def chat_create_table(self):
        self.send(
            "tableCreate", {"name": f"{self.convention_name} bots", "maxPlayers": 6}
        )

    def chat_set_variant(self, variant_name: str):
        if variant_name is not None:
            for table in self.tables.values():
                if self.username in table["players"]:
                    self.send(
                        "tableSetVariant",
                        {
                            "tableID": table["id"],
                            "options": {"variantName": variant_name},
                        },
                    )

    def chat_start(self):
        for table in self.tables.values():
            if self.username in table["players"]:
                self.send("tableStart", {"tableID": table["id"]})

    def chat_restart(self):
        for table in self.tables.values():
            if self.username in table["players"]:
                self.s
                self.send("tableRestart", {"tableID": table["id"], "hidePregame": True})

    def chat_terminate(self, table_id=None):
        if table_id is None:
            for table in self.tables.values():
                if self.username in table["players"]:
                    table_id = table["id"]

        self.send("terminateTable", {"tableID": table_id})

    def table(self, data):
        self.tables[data["id"]] = data
        if (
            self.bot_to_join is not None
            and self.bot_to_join != "create"
            and self.bot_to_join in data["players"]
        ):
            self.send("tableJoin", {"tableID": data["id"]})

    def table_list(self, data_list):
        for data in data_list:
            self.table(data)

    def table_gone(self, data):
        del self.tables[data["tableID"]]

    def table_start(self, data):
        # The server has told us that a game that we are in is starting
        # So, the next step is to request some high-level information about the
        # game (e.g. number of players)
        # The server will respond with an "init" command
        self.send("getGameInfo1", {"tableID": data["tableID"]})

    # -------------------------------
    # Website Command Handlers (Game)
    # -------------------------------

    def init(self, data):
        print("Init data:")
        print(data)
        print()

        """
        {
            'tableID': 29600,
            'playerNames': ['yagami_green', 'yagami_light', 'yagami_blue'],
            'ourPlayerIndex': 2, 'spectating': False, 'shadowing': False, 'replay': False,
            'databaseID': -1, 'hasCustomSeed': False, 'seed': 'p3v177s1',
            'datetimeStarted': '2023-07-03T20:36:19.812308097Z', 'datetimeFinished': '0001-01-01T00:00:00Z',
            'options': {
                'numPlayers': 3, 'startingPlayer': 0, 'variantID': 0, 'variantName': 'Omni (5 Suits)',
                'timed': False, 'timeBase': 0, 'timePerTurn': 0, 'speedrun': False, 'cardCycle': False,
                'deckPlays': False, 'emptyClues': False, 'oneExtraCard': False, 'oneLessCard': False,
                'allOrNothing': False, 'detrimentalCharacters': False
            }, 'characterAssignments': [], 'characterMetadata': [], 'sharedReplay': False,
            'sharedReplayLeader': 'yagami_light', 'sharedReplaySegment': 0, 'sharedReplayEffMod': 0,
            'paused': False, 'pausePlayerIndex': -1, 'pauseQueued': False
        }
        """

        self.action_time = False
        self.everyone_connected = False

        # Make a new game state and store it on the "games" dictionary

        state = self.game_state_cls(
            variant_name=data["options"]["variantName"],
            player_names=data["playerNames"],
            our_player_index=data["ourPlayerIndex"],
        )
        self.games[data["tableID"]] = state

        # At this point, the JavaScript client would have enough information to
        # load and display the game UI; for our purposes, we do not need to
        # load a UI, so we can just jump directly to the next step
        # Now, we request the specific actions that have taken place thus far
        # in the game (which will come in a "gameActionList")
        self.send("getGameInfo2", {"tableID": data["tableID"]})

    def _go(self, data):
        if data["tableID"] not in self.games:
            print("NO STATE FOUND FOR TABLE ID = " + str(data["tableID"]) + "!")
            return

        state = self.games[data["tableID"]]
        if (
            (state.current_player_index == state.our_player_index)
            & self.action_time
            & self.everyone_connected
        ):
            print("Player " + str(state.our_player_index) + " DECIDING ACTION!")
            self.decide_action(data["tableID"])
            self.action_time = False

    def game_action(self, data):
        # We just received a new action for an ongoing game
        self.handle_action(data["action"], data["tableID"])
        self._go(data)

    def game_action_list(self, data):
        for action in data["list"]:
            self.handle_action(action, data["tableID"])

        # Let the server know that we have finished "loading the UI"
        # (so that our name does not appear as red / disconnected)
        self.send("loaded", {"tableID": data["tableID"]})
        self._go(data)

    def handle_action(self, data, table_id):
        _type = data["type"]
        print(f'debug: got a game action of "{_type}" for table {table_id}: {data}')

        # Local variables
        state = self.games[table_id]

        if data["type"] == "draw":
            card = state.handle_draw(
                data["playerIndex"], data["order"], data["suitIndex"], data["rank"]
            )

        elif data["type"] == "play":
            state.print()
            state.handle_play(
                data["playerIndex"], data["order"], data["suitIndex"], data["rank"]
            )

        elif data["type"] == "discard":
            state.print()
            state.handle_discard(
                data["playerIndex"], data["order"], data["suitIndex"], data["rank"]
            )

        elif data["type"] == "clue":
            state.print()
            state.handle_clue(
                data["giver"],
                data["target"],
                data["clue"]["type"],
                data["clue"]["value"],
                data["list"],
            )

        elif data["type"] == "turn":
            state.turn = data["num"]
            state.current_player_index = data["currentPlayerIndex"]

        elif data["type"] == "strike":
            state.bombs = data["num"]

        elif data["type"] == "status":
            state.clue_tokens = data["clues"]

    def database_id(self, data):
        # Games are transformed into shared replays after they are completed
        # The server sends a "databaseID" message when the game has ended
        # Use this as a signal to leave the shared replay
        self.send(
            "tableUnattend",
            {
                "tableID": data["tableID"],
            },
        )

        # Delete the game state for the game to free up memory
        del self.games[data["tableID"]]

    def connected(self, data):
        print("Connected: " + str(data))
        self.everyone_connected = sum(data["list"]) == len(data["list"])
        print("self.everyone_connected = " + str(self.everyone_connected))

    def clock(self, data):
        """
        {
            'tableID': 2345, 'times': [-2268, -1015, -1039], 'activePlayerIndex': 1,
            'timeTaken': 0
        }
        """
        self.action_time = True
        self._go(data)

    def user(self, data):
        """
        {
            'userID': 81697, 'name': 'kingCLUE', 'status': 0, 'tableID': 0,
            'hyphenated': False, 'inactive': False
        }
        """
        pass

    def note_list_player(self, data):
        print("Note List Player: " + str(data))

    def chat_typing(self, data):
        print("Chat Typing: ", str(data))
        self.action_time = True
        self._go(data)

    def play(self, order, table_id):
        print(f"Playing order: {order}")
        self.send("action", {"tableID": table_id, "type": ACTION.PLAY, "target": order})

    def discard(self, order, table_id):
        print(f"Discarding order: {order}")
        self.send(
            "action", {"tableID": table_id, "type": ACTION.DISCARD, "target": order}
        )

    def clue(self, target_index, clue_type, clue_value, table_id):
        _type = {COLOR_CLUE: ACTION.COLOR_CLUE, RANK_CLUE: ACTION.RANK_CLUE}[clue_type]
        print(f"Giving {_type._name_} with value {clue_value} to {target_index}")
        self.send(
            "action",
            {
                "tableID": table_id,
                "type": _type,
                "target": target_index,
                "value": clue_value,
            },
        )

    def write_note(self, table_id, order, note):
        self.send("note", {"tableID": table_id, "order": order, "note": note})

    def decide_action(self, table_id):
        # The server expects to be told about actions in the following format:
        # https://github.com/Hanabi-Live/hanabi-live/blob/main/server/src/command.go
        state = self.games[table_id]
        if isinstance(state, EncoderGameState):
            self.encoder(state, table_id)
        elif isinstance(state, HGroupGameState):
            self.hgroup(state, table_id)
        else:
            raise ValueError(type(state))

        for order, note in state.notes.items():
            self.write_note(table_id, order, note)

    def hgroup(self, state: HGroupGameState, table_id: int):
        good_actions = {
            player_index: state.get_good_actions(player_index)
            for player_index in range(state.num_players)
        }
        my_good_actions = good_actions[state.our_player_index]
        next_player_good_actions = good_actions[state.next_player_index]
        print(f"{state.our_player_name} POV - good actions:")
        for player_index, orders in good_actions.items():
            print(player_index, orders)

        next_player_has_safe_action = False
        my_chop_order = state.get_chop_order(state.our_player_index)
        np_chop_order = state.get_chop_order(state.next_player_index)

        for action_type, orders in next_player_good_actions.items():
            if action_type == "seen_in_other_hand":
                # TODO: handle this at later levels
                continue
            if len(orders):
                next_player_has_safe_action = True
                break

        if not next_player_has_safe_action and state.clue_tokens > 0:
            if np_chop_order is not None:
                np_chop = state.get_card(np_chop_order)
                if (np_chop.suit_index, np_chop.rank) in state.playables:
                    self.clue(
                        state.next_player_index,
                        COLOR_CLUE,
                        np_chop.suit_index,
                        table_id,
                    )
                    return
                elif (np_chop.suit_index, np_chop.rank) in state.criticals:
                    self.clue(
                        state.next_player_index, RANK_CLUE, np_chop.rank, table_id
                    )
                    return

        # play if nothing urgent to do
        if len(my_good_actions["playable"]):
            # sort playables by lowest possible rank of candidates
            sorted_playables = sorted(
                my_good_actions["playable"],
                key=lambda order: min([x[1] for x in state.get_candidates(order)]),
            )
            playable_fives = [
                order
                for order in my_good_actions["playable"]
                if min([x[1] for x in state.get_candidates(order)]) == 5
            ]
            if len(playable_fives):
                self.play(playable_fives[0], table_id)
                return

            unique_playables = [
                order
                for order in sorted_playables
                if order not in my_good_actions["dupe_in_other_hand"]
            ]
            if len(unique_playables):
                self.play(unique_playables[0], table_id)
                return

            # all the playables we have are duped in someone else's hand
            # figure out where the duped card is and how to best resolve it
            for playable_order in sorted_playables:
                playable_candidates = state.get_candidates(playable_order)
                if state.pace <= state.num_players - 2:
                    print("PACE IS TOO LOW, NEED TO PLAY!!!")
                    self.play(playable_order, table_id)
                    return

                if len(playable_candidates) >= 2:
                    print("IDK WHAT THIS IS BUT ITS DUPED")
                    self.discard(playable_order, table_id)
                    return

                suit_index, rank = list(playable_candidates)[0]
                for player_index, hand in state.hands.items():
                    if player_index == state.our_player_index:
                        continue

                    for i, card in enumerate(hand):
                        if (suit_index, rank) != (card.suit_index, card.rank):
                            continue

                        candidates = state.all_candidates_list[player_index][i]
                        candidates_minus_my_play = candidates.difference(
                            {(suit_index, rank)}
                        )
                        if state.is_trash(candidates_minus_my_play):
                            print("OTHER GUY WILL KNOW ITS TRASH AFTER I PLAY THIS")
                            self.play(playable_order, table_id)
                            return

                        what_other_guy_sees = state.get_all_other_players_clued_cards(
                            player_index
                        )
                        unique_candidates_after_my_play = (
                            candidates_minus_my_play.difference(what_other_guy_sees)
                        )
                        if not len(unique_candidates_after_my_play) or state.is_trash(
                            unique_candidates_after_my_play
                        ):
                            print("OTHER GUY WILL KNOW ITS DUPED AFTER I PLAY THIS")
                            self.play(playable_order, table_id)
                            return

        if state.clue_tokens < 8:
            for trashable in [
                "trash",
                "dupe_in_own_hand",
                "dupe_in_other_hand",
                "dupe_in_other_hand_or_trash",
            ]:
                if len(my_good_actions[trashable]):
                    self.discard(my_good_actions[trashable][0], table_id)
                    return

            self.discard(my_chop_order, table_id)
            return

        if np_chop_order is not None:
            burn_clue_card = state.get_card(np_chop_order)
        else:
            burn_clue_card = state.hands[state.next_player_index][0]
        self.clue(state.next_player_index, RANK_CLUE, burn_clue_card.rank, table_id)

    def encoder(self, state: EncoderGameState, table_id: int):
        # TODO: implement elim
        # TODO: implement logic for other variants
        # TODO: improve clue selection when multiple legal clues available

        good_actions = {
            player_index: state.get_good_actions(player_index)
            for player_index in range(state.num_players)
        }
        my_good_actions = good_actions[state.our_player_index]
        print(state.our_player_name + " good actions:")
        for action_type, orders in good_actions.items():
            print(action_type, orders)

        if len(my_good_actions["playable"]):
            # sort playables by lowest possible rank of candidates
            sorted_playables = sorted(
                my_good_actions["playable"],
                key=lambda order: min([x[1] for x in state.get_candidates(order)]),
            )
            playable_fives = [
                order
                for order in my_good_actions["playable"]
                if min([x[1] for x in state.get_candidates(order)]) == 5
            ]
            if len(playable_fives):
                self.play(playable_fives[0], table_id)
                return

            unique_playables = [
                order
                for order in sorted_playables
                if order not in my_good_actions["dupe_in_other_hand"]
            ]
            if len(unique_playables):
                self.play(unique_playables[0], table_id)
                return

            # all the playables we have are duped in someone else's hand
            # figure out where the duped card is and how to best resolve it
            for playable_order in sorted_playables:
                playable_candidates = state.get_candidates(playable_order)
                if len(playable_candidates) >= 2:
                    print("TOO MANY CANDIDATES TO WORRY ABOUT, PLAYING THIS")
                    self.play(playable_order, table_id)
                    return

                suit_index, rank = list(playable_candidates)[0]
                for player_index, hand in state.hands.items():
                    if player_index == state.our_player_index:
                        continue

                    for i, card in enumerate(hand):
                        if (suit_index, rank) != (card.suit_index, card.rank):
                            continue

                        candidates = state.all_candidates_list[player_index][i]
                        candidates_minus_my_play = candidates.difference(
                            {(suit_index, rank)}
                        )
                        if state.is_trash(candidates_minus_my_play):
                            print("OTHER GUY WILL KNOW ITS TRASH AFTER I PLAY THIS")
                            self.play(playable_order, table_id)
                            return

                        what_other_guy_sees = (
                            state.get_all_other_players_hat_clued_cards(player_index)
                        )
                        unique_candidates_after_my_play = (
                            candidates_minus_my_play.difference(what_other_guy_sees)
                        )
                        if not len(unique_candidates_after_my_play) or state.is_trash(
                            unique_candidates_after_my_play
                        ):
                            print("OTHER GUY WILL KNOW ITS DUPED AFTER I PLAY THIS")
                            self.play(playable_order, table_id)
                            return

            if state.pace <= state.num_players - 2:
                print("PACE IS TOO LOW, NEED TO PLAY!!!")
                self.play(sorted_playables[0], table_id)
            else:
                print("NO DUPES WILL DEFINITELY RESOLVE, GDing this instead")
                self.discard(sorted_playables[0], table_id)
            return

        if len(my_good_actions["yoloable"]) and (
            state.bombs <= 1 or state.pace <= state.num_players - 3
        ):
            self.play(my_good_actions["yoloable"][0], table_id)
            return

        lnhcs = state.get_leftmost_non_hat_clued_cards()
        num_useful_cards = 0
        for card in lnhcs:
            if card is None:
                continue
            if (card.suit_index, card.rank) in state.trash:
                continue
            num_useful_cards += 1

        # clues that get a lot of useful cards are good
        legal_hat_clues = state.get_legal_clues()
        if 0 <= state.score_pct < 0.24:
            token_threshold = 2
            num_useful_cards_touched = int(0.78 * min(4, state.num_players - 1))
        elif 0.24 <= state.score_pct < 0.48:
            token_threshold = 2
            num_useful_cards_touched = int(0.68 * min(4, state.num_players - 1))
        elif 0.48 <= state.score_pct < 0.72:
            token_threshold = 2
            num_useful_cards_touched = int(0.58 * min(4, state.num_players - 1))
        else:
            token_threshold = 2
            num_useful_cards_touched = int(0.48 * min(4, state.num_players - 1))

        if (
            state.clue_tokens >= token_threshold
            and num_useful_cards >= num_useful_cards_touched
        ):
            for (
                clue_value,
                clue_type,
                target_index,
            ), cards_touched in legal_hat_clues.items():
                print(
                    "USEFUL CLUE! Score pct =",
                    round(state.score_pct, 3),
                    ", we see",
                    str(lnhcs),
                )
                self.clue(target_index, clue_type, clue_value, table_id)
                return

        # basic stall in endgame
        if state.clue_tokens > 0 and (state.pace < 3 or state.num_cards_in_deck == 1):
            for (
                clue_value,
                clue_type,
                target_index,
            ), cards_touched in legal_hat_clues.items():
                print("STALL CLUE!")
                self.clue(target_index, clue_type, clue_value, table_id)
                return

        # basic stall in endgame
        if state.clue_tokens >= state.num_players and (
            state.num_cards_in_deck <= state.num_players / 2
        ):
            for (
                clue_value,
                clue_type,
                target_index,
            ), cards_touched in legal_hat_clues.items():
                print("STALL CLUE 2!")
                self.clue(target_index, clue_type, clue_value, table_id)
                return

        # discard if nothing better to do
        if state.clue_tokens < 8:
            if len(my_good_actions["trash"]):
                print("X TRASH")
                self.discard(my_good_actions["trash"][0], table_id)
                return
            if len(my_good_actions["dupe_in_own_hand"]):
                print("X DUPE_IN_OWN_HAND")
                self.discard(my_good_actions["dupe_in_own_hand"][0], table_id)
                return
            if len(my_good_actions["dupe_in_other_hand"]):
                print("X DUPE_IN_OTHER_HAND")
                self.discard(my_good_actions["dupe_in_other_hand"][0], table_id)
                return
            if len(my_good_actions["dupe_in_other_hand_or_trash"]):
                print("X DUPE_IN_OTHER_HAND_OR_TRASH")
                self.discard(
                    my_good_actions["dupe_in_other_hand_or_trash"][0], table_id
                )
                return

        # unless we have no safe actions
        if state.clue_tokens > 0 and len(legal_hat_clues):
            for (
                clue_value,
                clue_type,
                target_index,
            ), cards_touched in legal_hat_clues.items():
                print("CLUE BECAUSE NO SAFE ACTION!")
                self.clue(target_index, clue_type, clue_value, table_id)
                return

        if state.clue_tokens < 8:
            if len(my_good_actions["seen_in_other_hand"]):
                print("DISCARDING CARD SEEN BUT NOT TOUCHED!")
                self.discard(my_good_actions["seen_in_other_hand"][0], table_id)
                return

            for i, candidates in enumerate(state.our_candidates):
                if state.our_hand[-i - 1].order not in state.hat_clued_card_orders:
                    print("SACRIFICING NON HAT CLUED SLOT " + str(i) + "!")
                    self.discard(state.our_hand[-i - 1].order, table_id)
                    return

            for i, candidates in enumerate(state.our_candidates):
                if (
                    not len(candidates.intersection(state.criticals))
                    or i == len(state.our_candidates) - 1
                ):
                    print("SACRIFICING SLOT " + str(len(state.our_hand) - i - 1) + "!")
                    self.discard(state.our_hand[i].order, table_id)
                    return
        else:
            for i, candidates in enumerate(state.our_candidates):
                if (
                    not len(candidates.intersection(state.criticals))
                    or i == len(state.our_candidates) - 1
                ):
                    print(
                        "STALL BOMBING SLOT " + str(len(state.our_hand) - i - 1) + "!"
                    )
                    self.play(state.our_hand[i].order, table_id)
                    return

    # -----------
    # Subroutines
    # -----------

    def chat_reply(self, message, recipient):
        self.send(
            "chatPM",
            {
                "msg": message,
                "recipient": recipient,
                "room": "lobby",
            },
        )

    def send(self, command, data):
        if not isinstance(data, dict):
            data = {}
        self.ws.send(command + " " + json.dumps(data))

    def remove_card_from_hand(self, state, player_index, order):
        hand = state.hands[player_index]
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
        del state.all_candidates_list[player_index][card_index]
        return card
