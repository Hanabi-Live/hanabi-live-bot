# Imports (standard library)
import json

# Imports (3rd-party)
import websocket

# Imports (local application)
from constants import ACTION
from game_state import GameState


class HanabiClient:
    def __init__(self, url, cookie):
        # Initialize all class variables
        self.commandHandlers = {}
        self.tables = {}
        self.username = ""
        self.ws = None
        self.games = {}

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

        # Start the WebSocket client
        print('Connecting to "' + url + '".')

        self.ws = websocket.WebSocketApp(
            url,
            on_message=lambda ws, message: self.websocket_message(ws, message),
            on_error=lambda ws, error: self.websocket_error(ws, error),
            on_open=lambda ws: self.websocket_open(ws),
            on_close=lambda ws: self.websocket_close(ws),
            cookie=cookie,
        )
        self.ws.run_forever()

    # ------------------
    # WebSocket Handlers
    # ------------------

    def websocket_message(self, ws, message):
        # WebSocket messages from the server come in the format of:
        # commandName {"data1":"data2"}
        # For more information, see:
        # https://github.com/Zamiell/hanabi-live/blob/master/src/websocketMessage.go
        result = message.split(" ", 1)  # Split it into two things
        if len(result) != 1 and len(result) != 2:
            print("error: received an invalid WebSocket message:")
            print(message)
            return

        command = result[0]
        try:
            data = json.loads(result[1])
        except:
            print(
                'error: the JSON data for the command of "' + command + '" was invalid'
            )
            return

        if command in self.commandHandlers:
            print('debug: got command "' + command + '"')
            try:
                self.commandHandlers[command](data)
            except Exception as e:
                print('error: command handler for "' + command + '" failed:', e)
                return
        else:
            print('debug: ignoring command "' + command + '"')

    def websocket_error(self, ws, error):
        print("Encountered a WebSocket error:", error)

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
        data["msg"] = data["msg"][1:]  # Remove the slash

        # We want to split it into two things
        result = data["msg"].split(" ", 1)
        command = result[0]

        if command == "join":
            self.chat_join(data)
        else:
            self.chat_reply("That is not a valid command.", data["who"])

    def chat_join(self, data):
        # Someone sent a private message to the bot and requested that we join
        # their game
        # Find the table that the current user is currently in
        table_id = None
        for table in self.tables.values():
            # Ignore games that have already started (and shared replays)
            if table["running"]:
                continue

            if data["who"] in table["players"]:
                if len(table["players"]) == 6:
                    msg = (
                        "Your game is full. Please make room for me before "
                        "requesting that I join your game."
                    )
                    self.chat_reply(msg, data["who"])
                    return

                table_id = table["id"]
                break

        if table_id is None:
            self.chat_reply(
                "Please create a table first before requesting "
                "that I join your game.",
                data["who"],
            )
            return

        self.send(
            "tableJoin",
            {
                "tableID": table_id,
            },
        )

    def table(self, data):
        self.tables[data["id"]] = data

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
        self.send(
            "getGameInfo1",
            {
                "tableID": data["tableID"],
            },
        )

    # -------------------------------
    # Website Command Handlers (Game)
    # -------------------------------

    def init(self, data):
        # At the beginning of the game, the server sends us some high-level
        # data about the game, including the names and ordering of the players
        # at the table

        # Make a new game state and store it on the "games" dictionary
        state = GameState()
        self.games[data["tableID"]] = state

        state.player_names = data["playerNames"]
        state.our_player_index = data["ourPlayerIndex"]

        # Initialize the hands for each player (an array of cards)
        for _ in range(len(state.player_names)):
            state.hands.append([])

        # Initialize the play stacks
        """
        This is hard coded to 5 because there 5 suits in a no variant game
        The website supports variants that have 3, 4, and 6 suits
        TODO This code should compare "data['variant']" to the "variants.json"
        file in order to determine the correct amount of suits
        https://raw.githubusercontent.com/Zamiell/hanabi-live/master/public/js/src/data/variants.json
        """
        for _ in range(5):
            state.play_stacks.append([])

        # At this point, the JavaScript client would have enough information to
        # load and display the game UI; for our purposes, we do not need to
        # load a UI, so we can just jump directly to the next step
        # Now, we request the specific actions that have taken place thus far
        # in the game
        self.send(
            "getGameInfo2",
            {
                "tableID": data["tableID"],
            },
        )

    def game_action(self, data):
        # Local variables
        state = self.games[data["tableID"]]

        # We just received a new action for an ongoing game
        self.handle_action(data["action"], data["tableID"])

        if state.current_player_index == state.our_player_index:
            self.decide_action(data["tableID"])

    def game_action_list(self, data):
        # Local variables
        state = self.games[data["tableID"]]

        # We just received a list of all of the actions that have occurred thus
        # far in the game
        for action in data["list"]:
            self.handle_action(action, data["tableID"])

        if state.current_player_index == state.our_player_index:
            self.decide_action(data["tableID"])

        # Let the server know that we have finished "loading the UI"
        # (so that our name does not appear as red / disconnected)
        self.send(
            "loaded",
            {
                "tableID": data["tableID"],
            },
        )

    def handle_action(self, data, table_id):
        print(
            'debug: got a game action of "'
            + data["type"]
            + '" for table '
            + str(table_id)
        )

        # Local variables
        state = self.games[table_id]

        if data["type"] == "draw":
            # Add the newly drawn card to the player's hand
            hand = state.hands[data["playerIndex"]]
            hand.append(
                {
                    "order": data["order"],
                    "suit_index": data["suitIndex"],
                    "rank": data["rank"],
                }
            )

        elif data["type"] == "play":
            seat = data["which"]["index"]
            order = data["which"]["order"]
            card = self.remove_card_from_hand(state, seat, order)
            if card is not None:
                # TODO Add the card to the play stacks
                pass

        elif data["type"] == "discard":
            seat = data["which"]["index"]
            order = data["which"]["order"]
            card = self.remove_card_from_hand(state, seat, order)
            if card is not None:
                # TODO Add the card to the play stacks
                pass

            # Discarding adds a clue
            if not data["failed"]:  # Misplays are represented as discards
                state.clue_tokens += 1

        elif data["type"] == "clue":
            # Each clue costs one clue token
            state.clue_tokens -= 1

            # TODO We might also want to update the state of cards that are
            # "touched" by the clue

        elif data["type"] == "turn":
            state.turn = data["num"]
            state.current_player_index = data["currentPlayerIndex"]

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

    # ------------
    # AI functions
    # ------------

    def decide_action(self, table_id):
        # Local variables
        state = self.games[table_id]

        # The server expects to be told about actions in the following format:
        # https://github.com/Zamiell/hanabi-live/blob/master/src/command_action.go

        # Decide what to do
        if state.clue_tokens > 0:
            # There is a clue available,
            # so give a rank clue to the next person's slot 1 card

            # Target the next player
            target_index = state.our_player_index + 1
            if target_index > len(state.players) - 1:
                target_index = 0

            # Cards are added oldest to newest,
            # so "slot 1" is the final element in the list
            target_hand = state.hands[target_index]
            slot_1_card = target_hand[-1]

            self.send(
                "action",
                {
                    "tableID": table_id,
                    "type": ACTION.RANK_CLUE,
                    "target": target_index,
                    "value": slot_1_card["rank"],
                },
            )
        else:
            # There are no clues available, so discard our oldest card
            oldest_card = state.hands[state.our_player_index][0]
            self.send(
                "action",
                {
                    "tableID": table_id,
                    "type": ACTION.DISCARD,
                    "target": oldest_card["order"],
                },
            )

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
        print('debug: sent command "' + command + '"')

    # "seat" is the index of the player
    def remove_card_from_hand(self, state, seat, order):
        hand = state.hands[seat]
        card_index = -1
        for i in range(len(hand)):
            card = hand[i]
            if card["order"] == order:
                card_index = i
        if card_index == -1:
            print(
                "error: unable to find card with order " + str(order) + " in"
                "the hand of player " + str(seat)
            )
            return None
        card = hand[card_index]
        del hand[card_index]
        return card
