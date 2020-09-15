#!/usr/bin/env python

# An example reference bot for the Hanab Live website
# Written by Zamiel

# The "dotenv" module does not work in Python 2
import sys

if sys.version_info < (3, 0):
    print("This script requires Python 3.x.")
    sys.exit(1)

# Imports (standard library)
import os

# Imports (3rd-party)
import dotenv
import requests

# Imports (local application)
from hanabi_client import HanabiClient


# Authenticate, login to the WebSocket server, and run forever
def main():
    # Load environment variables from the ".env" file
    dotenv.load_dotenv()

    use_localhost = os.getenv("USE_LOCALHOST")
    if use_localhost == "":
        print('error: "USE_LOCALHOST" is blank in the ".env" file')
        sys.exit(1)
    if use_localhost == "true":
        use_localhost = True
    elif use_localhost == "false":
        use_localhost = False
    else:
        print(
            'error: "USE_LOCALHOST" should be set to either "true" or '
            '"false" in the ".env" file'
        )
        sys.exit(1)

    username = os.getenv("HANABI_USERNAME")
    if username == "":
        print('error: "HANABI_USERNAME" is blank in the ".env" file')
        sys.exit(1)

    password = os.getenv("HANABI_PASSWORD")
    if password == "":
        print('error: "HANABI_PASSWORD" is blank in the ".env" file')
        sys.exit(1)

    # Get an authenticated cookie by POSTing to the login handler
    if use_localhost:
        protocol = "http"
        ws_protocol = "ws"
        host = "localhost"
    else:
        protocol = "https"
        ws_protocol = "wss"
        host = "hanab.live"
    path = "/login"
    ws_path = "/ws"
    url = protocol + "://" + host + path
    ws_url = ws_protocol + "://" + host + ws_path
    print('Authenticating to "' + url + '" with a username of "' + username + '".')
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
        print("Failed to parse the cookie from the authentication response " "headers:")
        print(resp.headers)
        sys.exit(1)

    HanabiClient(ws_url, cookie)


if __name__ == "__main__":
    main()
