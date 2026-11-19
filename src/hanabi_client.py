# Imports (standard library)
import json
import logging

# Imports (3rd-party)
import websocket

# Imports (local application)
from constants import MAX_CLUE_NUM, MAX_RANK
from game_state import GameState
from util import printf

# A handler that fails is logged with its traceback, and the bot keeps running.
log = logging.getLogger(__name__)


class HanabiClient:
    def __init__(self, url, cookie):
        # Initialize all class variables.
        self.event_handlers = {}
        self.tables = {}
        self.username = ""
        self.ws = None
        self.games = {}

        # Every request has an ID that we choose. The server answers each
        # request once, with a reply that repeats its ID. We keep a callback
        # for the requests whose reply we need.
        self.next_request_id = 1
        self.reply_handlers = {}

        # Initialize the handlers of the events that the server sends on its
        # own (for the lobby).
        self.event_handlers["welcome"] = self.welcome
        self.event_handlers["warning"] = self.notice
        self.event_handlers["error"] = self.notice
        self.event_handlers["chat"] = self.chat
        self.event_handlers["table"] = self.table
        self.event_handlers["tableRemoved"] = self.table_removed
        self.event_handlers["tableJoined"] = self.table_joined

        # Initialize the handlers of the events that the server sends on its
        # own (for the game).
        self.event_handlers["gameState"] = self.game_state
        self.event_handlers["gameEvent"] = self.game_event
        self.event_handlers["gameFinished"] = self.game_finished

        # Start the WebSocket client.
        printf('Connecting to "' + url + '".')

        self.ws = websocket.WebSocketApp(
            url,
            on_message=lambda ws, message: self.websocket_message(ws, message),
            on_error=lambda ws, error: self.websocket_error(ws, error),
            on_open=lambda ws: self.websocket_open(ws),
            on_close=lambda ws, close_status_code, close_msg: self.websocket_close(ws),
            cookie=cookie,
        )
        self.ws.run_forever()

    # ------------------
    # WebSocket Handlers
    # ------------------

    def websocket_message(self, ws, message):
        # Each WebSocket message from the server is one JSON object. An event
        # that the server sends on its own looks like:
        # {"event": "table", "data": {...}}
        # A reply to one of our requests looks like:
        # {"reply": 1, "data": {...}} or {"reply": 1, "error": {...}}
        # For more information, see:
        # https://github.com/Hanabi-Live/hanabi-live/blob/main/packages/data/src/functions/frames.ts
        try:
            frame = json.loads(message)
        except ValueError:
            printf("error: a message from the server was not valid JSON")
            return

        if "event" in frame:
            self.handle_event(frame["event"], frame.get("data"))
        elif "reply" in frame:
            self.handle_reply(frame["reply"], frame.get("data"), frame.get("error"))
        else:
            printf("error: a message from the server was not an event or a reply")

    def handle_event(self, event, data):
        if event not in self.event_handlers:
            printf('debug: ignoring event "' + event + '"')
            return

        printf('debug: got event "' + event + '"')
        try:
            self.event_handlers[event](data)
        except Exception:
            log.exception('event handler for "%s" failed', event)

    def handle_reply(self, request_id, data, error):
        handler = self.reply_handlers.pop(request_id, None)

        if error is not None:
            # The server refused our request.
            printf("error: request " + str(request_id) + " failed:", error)
            return

        if handler is not None:
            try:
                handler(data)
            except Exception:
                log.exception("reply handler for request %s failed", request_id)

    def websocket_error(self, ws, error):
        printf("Encountered a WebSocket error:", error)

    def websocket_close(self, ws):
        printf("WebSocket connection closed.")

    def websocket_open(self, ws):
        printf("Successfully established WebSocket connection.")

    # ----------------------
    # Event Handlers (Lobby)
    # ----------------------

    def welcome(self, data):
        # The "welcome" event is the first message that the server sends us
        # once we have established a connection. It contains our username,
        # settings, and so forth.
        self.username = data["username"]

        # It also lists the tables in the lobby. The "table" and
        # "tableRemoved" events change the list after that.
        self.tables = {table["tableId"]: table for table in data["tables"]}

        # If we were disconnected in the middle of a game, return to it.
        for table_id in data["playingAtTables"]:
            self.send("tableReattend", {"tableId": table_id})

    def notice(self, data):
        # Either we have done something wrong, or something has gone wrong on
        # the server.
        printf(data["message"])

    def chat(self, data):
        # We only care about private messages to us.
        kind = data["kind"]
        if kind["type"] != "private" or kind["recipient"] != self.username:
            return

        # We only care about private messages from users. (The server can also
        # send them.)
        author = kind["author"]
        if author["type"] != "user":
            return
        who = author["username"]

        # We only care about private messages that start with a forward slash.
        text = data["text"]
        if not text.startswith("/"):
            return
        text = text[1:]  # Remove the slash.

        # We want to split it into two things.
        result = text.split(" ", 1)
        command = result[0]

        if command == "join":
            self.chat_join(who)
        else:
            msg = "That is not a valid command."
            self.chat_reply(msg, who)

    def chat_join(self, who):
        # Someone sent a private message to the bot and requested that we join
        # their game. Find the table that the current user is currently in.
        table_id = None
        for table in self.tables.values():
            # Ignore games that have already started (and shared replays).
            if table["phase"]["type"] != "pregame":
                continue

            if who in table["playerNames"]:
                if len(table["playerNames"]) >= table["settings"]["maxPlayers"]:
                    msg = "Your game is full. Please make room for me before requesting that I join your game."
                    self.chat_reply(msg, who)
                    return

                table_id = table["tableId"]
                break

        if table_id is None:
            msg = "Please create a table first before requesting that I join your game."
            self.chat_reply(msg, who)
            return

        self.send("tableJoin", {"tableId": table_id})

    def table(self, data):
        self.tables[data["tableId"]] = data

    def table_removed(self, data):
        self.tables.pop(data["tableId"], None)

    def table_joined(self, data):
        # The server has put us on the screen of a table: its pregame, its game
        # (which may have just started), or the replay of its finished game.
        table_id = data["tableId"]
        stage = data["stage"]

        if stage == "replay":
            # We have no use for replays.
            self.send("tableUnattend", {"tableId": table_id})
            return

        if stage not in ("justStarted", "playing"):
            return

        # The next step is to request some high-level information about the
        # game (e.g. number of players). The server will answer with the
        # game's setup.
        self.send(
            "gameInitLoad",
            {"tableId": table_id},
            lambda game_init: self.game_init(table_id, game_init),
        )

    # ---------------------
    # Event Handlers (Game)
    # ---------------------

    def game_init(self, table_id, data):
        # At the beginning of the game, the server sends us some high-level
        # data about the game, including the names and ordering of the players
        # at the table.
        mode = data["mode"]
        if mode["type"] != "playing":
            # We are not a player of this game.
            return

        # Make a new game state and store it on the "games" dictionary.
        state = GameState()
        self.games[table_id] = state

        state.player_names = data["playerNames"]
        state.our_player_index = mode["ourPlayerIndex"]

        # The first player always starts, and the server sends no "turn" event
        # before the first turn.
        state.current_player_index = 0

        # Initialize the hands for each player (an array of cards).
        for _ in range(len(state.player_names)):
            state.hands.append([])

        # Initialize the play stacks.
        """
        This is hard coded to 5 because there 5 suits in a no variant game
        The website supports variants that have 3, 4, and 6 suits
        TODO This code should compare "data['options']['variantId']" to the
        "variants.json" file in order to determine the correct amount of suits
        https://raw.githubusercontent.com/Hanabi-Live/hanabi-live/main/packages/game/src/json/variants.json
        """
        num_suits = 5
        for _ in range(num_suits):
            state.play_stacks.append([])

        # At this point, the JavaScript client would have enough information to
        # load and display the game UI. For our purposes, we do not need to
        # load a UI, so we can just jump directly to the next step. Now, we
        # request the events that have taken place thus far in the game (which
        # will come in a "gameState" event).
        self.send("gameStateLoad", {"tableId": table_id})

    def game_state(self, data):
        table_id = data["tableId"]
        state = self.games.get(table_id)
        if state is None:
            return

        # We just received all of the events that have occurred thus far in
        # the game.
        for event in data["events"]:
            self.handle_game_event(event, table_id)

        # Let the server know that we have finished "loading the UI" (so that
        # our name does not appear as red / disconnected).
        self.send("gameLoaded", {"tableId": table_id})

        if state.current_player_index == state.our_player_index:
            self.decide_action(table_id)

    def game_event(self, data):
        table_id = data["tableId"]
        state = self.games.get(table_id)
        if state is None:
            return

        # We just received the events of one move in an ongoing game, such as
        # a play, the draw after it, and the next turn.
        for event in data["events"]:
            self.handle_game_event(event, table_id)

            # A "turn" event is always the final event of a turn, so it is the
            # signal that it might now be our turn. (Checking after every event
            # could cause us to act twice.)
            if (
                event["type"] == "turn"
                and state.current_player_index == state.our_player_index
            ):
                self.decide_action(table_id)

    def handle_game_event(self, data, table_id):
        event_type = data["type"]
        printf(f'debug: got a game event of "{event_type}" for table {table_id}')

        state = self.games[table_id]

        if data["type"] == "draw":
            # Add the newly drawn card to the player's hand. We cannot see the
            # identity of our own cards.
            identity = data.get("identity", {})
            hand = state.hands[data["playerIndex"]]
            hand.append(
                {
                    "order": data["order"],
                    "suit_index": identity.get("suitIndex", -1),
                    "rank": identity.get("rank", -1),
                }
            )

        elif data["type"] == "play":
            player_index = data["playerIndex"]
            order = data["order"]
            card = self.remove_card_from_hand(state, player_index, order)
            if card is not None:
                # TODO Add the card to the play stacks.
                pass

            # Playing the last card of a suit gives a clue back.
            identity = data.get("identity", {})
            if identity.get("rank") == MAX_RANK and state.clue_tokens < MAX_CLUE_NUM:
                state.clue_tokens += 1

        elif data["type"] == "discard":
            player_index = data["playerIndex"]
            order = data["order"]
            card = self.remove_card_from_hand(state, player_index, order)
            if card is not None:
                # TODO Add the card to the discard stacks.
                pass

            # Discarding gives a clue back.
            state.clue_tokens += 1

        elif data["type"] == "misplay":
            # A play that fails discards the card and adds a strike, but does
            # not give a clue back.
            player_index = data["playerIndex"]
            order = data["order"]
            card = self.remove_card_from_hand(state, player_index, order)
            if card is not None:
                # TODO Add the card to the discard stacks.
                pass

        elif data["type"] == "clue":
            # Each clue costs one clue token.
            state.clue_tokens -= 1

            # TODO We might also want to update the state of cards that are
            # "touched" by the clue so that we can keep track of the positive
            # and negative information "on" the card.

        elif data["type"] == "turn":
            # A turn is comprised of one or more game events (e.g. play +
            # draw). The turn event will be the final thing sent on a turn,
            # which also includes the index of the new current player. (It has
            # no current player once the game has ended.)
            state.turn = data["turn"]
            state.current_player_index = data.get("currentPlayerIndex", -1)

    def game_finished(self, data):
        # Games are transformed into shared replays after they are completed.
        # The server sends a "gameFinished" event when the game has ended. Use
        # this as a signal to leave the shared replay.
        self.send("tableUnattend", {"tableId": data["tableId"]})

        # Delete the game state for the game to free up memory.
        self.games.pop(data["tableId"], None)

    # ------------
    # AI functions
    # ------------

    def decide_action(self, table_id):
        state = self.games[table_id]

        # The server expects to be told about actions in the following format:
        # https://github.com/Hanabi-Live/hanabi-live/blob/main/server/protocol/src/replay.rs

        # Decide what to do.
        if state.clue_tokens > 0:
            # There is a clue available, so give a rank clue to the next
            # person's slot 1 card.

            # Target the next player.
            target_index = state.our_player_index + 1
            if target_index > len(state.player_names) - 1:
                target_index = 0

            # Cards are added oldest to newest, so "slot 1" is the final
            # element in the list.
            target_hand = state.hands[target_index]
            slot_1_card = target_hand[-1]

            action = {
                "type": "clue",
                "receiverIndex": target_index,
                "clue": {"type": "rank", "rank": slot_1_card["rank"]},
            }
        else:
            # There are no clues available, so discard our oldest card.
            oldest_card = state.hands[state.our_player_index][0]
            action = {"type": "discard", "order": oldest_card["order"]}

        self.send("playerAction", {"tableId": table_id, "action": action})

    # -----------
    # Subroutines
    # -----------

    def chat_reply(self, message, recipient):
        self.send("chatPm", {"text": message, "recipient": recipient})

    def send(self, request, data, on_reply=None):
        # Each request is one JSON object with an ID that we choose. The server
        # answers it with a reply that repeats the ID.
        request_id = self.next_request_id
        self.next_request_id += 1
        if on_reply is not None:
            self.reply_handlers[request_id] = on_reply

        self.ws.send(json.dumps({"id": request_id, "request": request, "data": data}))
        printf('debug: sent request "' + request + '"')

    def remove_card_from_hand(self, state, player_index, order):
        hand = state.hands[player_index]
        card_index = -1
        for i in range(len(hand)):
            card = hand[i]
            if card["order"] == order:
                card_index = i
        if card_index == -1:
            printf(
                "error: unable to find card with order " + str(order) + " in "
                "the hand of player " + str(player_index)
            )
            return None
        card = hand[card_index]
        del hand[card_index]
        return card
