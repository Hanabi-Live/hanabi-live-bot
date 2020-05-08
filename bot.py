# An example bot for the Hanabi Live website
# Written by Zamiel

# Imports
import hashlib
import json
import os
import sys
import dotenv
import requests
import websocket

# Constants
# "use_localhost" should be true if running a local version of Hanabi Live,
# false if using the real website
use_localhost = True

# Authenticate, login to the Hanabi Live WebSocket server, and run forever
def main():
    # Load environment variables from the ".env" file
    dotenv.load_dotenv()
    username = os.getenv('HANABI_USERNAME')
    if username == '':
        print('error: "HANABI_USERNAME" is blank in the ".env" file')
        sys.exit(1)
    password = os.getenv('HANABI_PASSWORD')
    if password == '':
        print('error: "HANABI_PASSWORD" is blank in the ".env" file')
        sys.exit(1)

    # Get an authenticated cookie by POSTing to the login handler
    protocol = 'http'
    host = 'localhost'
    if not use_localhost:
        protocol = 'https'
        host = 'hanabi.live'
    path = '/login'
    url = protocol + '://' + host + path
    print('Authenticating to "' + url + '" with a username of "' + username + '".')
    resp = requests.post(url, {
        'username': username,
        'password': password,
        # This is normally the version of the JavaScript client,
        # but it will also accept "bot" as a valid version
        'version': 'bot',
    })

    # Handle failed authentication and other errors
    if resp.status_code != 200:
        print('Authentication failed:')
        print(resp.text)
        sys.exit(1)

    # Scrape the cookie from the response
    cookie = ''
    for header in resp.headers.items():
        if header[0] == 'Set-Cookie':
            cookie = header[1]
            break
    if cookie == '':
        print('Failed to parse the cookie from the authentication response headers:')
        ptint(resp.headers)
        sys.exit(1)

    HanabiClient(cookie)


class HanabiClient:
    def __init__(self, cookie):
        # Initialize all class variables (for the lobby)
        self.commandHandlers = {}
        self.tables = {}
        self.username = ''
        self.ws = None

        # Initialize all class variables (for the game state)
        self.clue_tokens = -1
        self.discard_pile = []
        self.hands = []
        self.our_index = -1
        self.play_stacks = []
        self.players = []
        self.turn = -1

        # Initialize the Hanabi Live command handlers (for the lobby)
        self.commandHandlers['welcome'] = self.welcome
        self.commandHandlers['chat'] = self.chat
        self.commandHandlers['table'] = self.table
        self.commandHandlers['tableList'] = self.table_list
        self.commandHandlers['tableGone'] = self.table_gone
        self.commandHandlers['tableStart'] = self.table_start

        # Initialize the Hanabi Live command handlers (for the game)
        self.commandHandlers['init'] = self.init
        self.commandHandlers['notify'] = self.notify
        self.commandHandlers['notifyList'] = self.notify_list

        # Start the WebSocket client
        protocol = 'ws'
        host = 'localhost'
        if not use_localhost:
            protocol = 'wss'
            host = 'hanabi.live'
        path = '/ws'
        url = protocol + '://' + host + path
        print('Connecting to "' + url + '".')

        self.ws = websocket.WebSocketApp(
            url,
            on_message = lambda ws, message: self.websocket_message(ws, message),
            on_error   = lambda ws, error:   self.websocket_error(ws, error),
            on_open    = lambda ws:          self.websocket_open(ws),
            on_close   = lambda ws:          self.websocket_close(ws),
            cookie     = cookie,
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
        result = message.split(' ', 1) # We want to split it into two things
        if len(result) != 1 and len(result) != 2:
            print('error: recieved an invalid WebSocket message:')
            print(message)
            return

        command = result[0]
        try:
            data = json.loads(result[1])
        except:
            print('error: the JSON data for the command of "' + command + '" was invalid')
            return

        print('debug: got command "' + command + '"')
        if command in self.commandHandlers:
            try:
                self.commandHandlers[command](data)
            except Exception as e:
                print('error: command handler for "' + command + '" failed:', e)
                return
        # (in a complete implementation, we might want handlers for every possible command;
        # for now, just ignore the commands that we don't care about)

    def websocket_error(self, ws, error):
        print('Encountered a WebSocket error:', error)

    def websocket_close(self, ws):
        print('WebSocket connection closed.')

    def websocket_open(self, ws):
        print('Successfully established WebSocket connection.')

    # ------------------------------------
    # Hanabi Live Command Handlers (Lobby)
    # ------------------------------------

    def welcome(self, data):
        # The "welcome" message is the first message that the server sends us
        # once we have established a connection
        # It contains our username, settings, and so forth
        self.username = data['username']

    def chat(self, data):
        # We only care about private messages
        if data['recipient'] != self.username:
            return

        # We only care about private messages that start with a forward slash
        if not data['msg'].startswith('/'):
            return
        data['msg'] = data['msg'][1:] # Remove the slash

        result = data['msg'].split(' ', 1) # We want to split it into two things
        command = result[0]

        if command == 'join':
            # TODO instead we can have the bot look through all the tables for the respective user,
            # which is more user-friendly (e.g. avoiding copy-pasting the table name every time)
            if len(result) < 1:
                self.chat_reply('You must provide the table name. e.g. /join wending invigoratingly condescend', data['who'])
                return

            # Find the table ID for this name
            table_name = result[1]
            table_id = -1
            for table in self.tables.values():
                if table['name'] == table_name:
                    table_id = table['id']
                    break
            if table_id == -1:
                self.chat_reply('The table "' + table_name + '" does not exist.', data['who'])
                return

            # Join it
            self.send('tableJoin', {
                'tableID': table_id,
            })

    def table(self, data):
        self.tables[data['id']] = data

    def table_list(self, data_list):
        for data in data_list:
            self.table(data)

    def table_gone(self, data):
        del self.tables[data['id']]

    def table_start(self, data):
        # The server has told us that a game that we are in is starting
        # So, the next step is to request some high-level information about the game
        # (e.g. number of players)
        # The server will respond with an "init" command
        self.send('getGameInfo1', {
            'tableID': data['tableID']),
        })

    # -----------------------------------
    # Hanabi Live Command Handlers (Game)
    # -----------------------------------

    def init(self, data):
        # At the beginning of the game,
        # the server sends us the names and ordering of the players at the table
        self.players = data['names']

        # Find our index
        for i in range(len(self.players)):
            player_name = self.players[i]
            if player_name == self.username:
                self.our_index = i
                break

        # Initialize the hands for each player
        self.hands = []
        for i in range(len(self.players)):
            self.hands.append([])

        # Initialize the play stacks and discard pile
        self.play_stacks = []
        for i in range(5):
            self.play_stacks.append([])
        self.discard_pile = []

        # At this point, the JavaScript client would have enough information to load and display the
        # game UI; for our purposes, we do not need to load a UI, so we can just jump directly to
        # the next step
        # Now, we request the specific actions that have taken place thus far in the game
        self.send('getGameInfo2', {
            'tableID': data['tableID'],
        })

    def notify(self, data):
        print('debug: got notify "' + data['type'] + '"')
        if data['type'] == 'draw':
            # Add the newly drawn card to the player's hand
            self.hands[data['who']].append({
                'order': data['order'],
                'suit': data['suit'],
                'rank': data['rank'],
            })
        elif data['type'] == 'play':
            # TODO add the card to the play stacks, etc.
            pass
        elif data['type'] == 'discard':
            # TODO add the card to the discard pile, etc.
            pass
        elif data['type'] == 'clue':
            # TODO update the game state, etc.
            pass
        elif data['type'] == 'turn':
            self.turn = data['num']
            if data['who'] == self.our_index:
                # It is our turn, so take an action
                self.decide_action()
        elif data['type'] == 'status':
            self.clue_tokens = data['clues']

    def notify_list(self, data_list):
        for data in data_list:
            self.notify(data)

    # ------------
    # AI functions
    # ------------

    def decide_action(self):
        # Decide what to do
        if self.clue_tokens > 0:
            # Give a clue to the next person's first card
            target_index = self.our_index + 1
            if target_index > len(self.players) - 1:
                target_index = 0

            # Cards are added oldest to newest, so "slot 1" is the final element in the list
            target_hand = self.hands[target_index]
            slot_1_card = target_hand[-1]

            self.send('action', {
                # See "actionType" and "clueType" constants at:
                # https://github.com/Zamiell/hanabi-live/blob/master/src/constants.go
                # TODO make this an enum
                'type': 0,
                'target': target_index,
                'clue': {
                    'type': 0,
                    'value': slot_1_card['rank'],
                }
            })
        else:
            # Discard our oldest card
            oldest_card = self.hands[self.our_index][0]
            self.send('action', {
                # See "actionType" constants at:
                # https://github.com/Zamiell/hanabi-live/blob/master/src/constants.go
                # TODO make this an enum
                'type': 2,
                'target': oldest_card['order'],
            })

    # -----------
    # Subroutines
    # -----------

    def chat_reply(self, message, recipient):
        self.send('chatPM', {
            'msg': message,
            'recipient': recipient,
            'room': 'lobby',
        })

    def send(self, command, data):
        self.ws.send(command + ' ' + json.dumps(data))
        print('debug: sent command "' + command + '"')

# ----
# Main
# ----

if __name__ == '__main__':
    main()
