#!/usr/bin/env python
import sys

import os
import json
import requests

from hanabi_client import HanabiClient


# Authenticate, login to the WebSocket server, and run forever
def run(username, bot_to_join):
    # Check to see if the ".env" file exists
    config_file = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), "config.json"
    )
    with open(config_file, "r") as f:
        config = json.load(f)

    use_localhost = config["use_localhost"]
    # Get an authenticated cookie by POSTing to the login handler
    if use_localhost:
        # Assume that we are not using a certificate if we are running a local
        # version of the server
        protocol = "http"
        ws_protocol = "ws"
        host = "localhost"
    else:
        # The official site uses HTTPS
        protocol = "https"
        ws_protocol = "wss"
        host = "hanab.live"

    path = "/login"
    ws_path = "/ws"
    url = protocol + "://" + host + path
    ws_url = ws_protocol + "://" + host + ws_path

    password = config["bots"][username]
    print(f'Authenticating to "{url}" with username = "{username}".')
    resp = requests.post(
        url,
        {
            "username": username,
            "password": password,
            # This is normally the version of the JavaScript client,
            # but it will also accept "bot" as a valid version
            "version": "bot",
        },
    )

    # Handle failed authentication and other errors
    if resp.status_code != 200:
        print("Authentication failed:")
        print(resp.text)
        sys.exit(1)

    # Scrape the cookie from the response
    cookie = ""
    for header in resp.headers.items():
        if header[0] == "Set-Cookie":
            cookie = header[1]
            break
    if cookie == "":
        print("Failed to parse the cookie from the authentication response headers:")
        print(resp.headers)
        sys.exit(1)

    convention = config["convention"]
    disconnect_on_game_end = config["disconnect_on_game_end"]
    HanabiClient(ws_url, cookie, bot_to_join, convention, disconnect_on_game_end)


if __name__ == "__main__":
    username = sys.argv[1]
    bot_to_join = sys.argv[2] if len(sys.argv) > 2 else None
    run(username, bot_to_join)
