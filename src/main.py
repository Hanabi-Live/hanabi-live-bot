#!/usr/bin/env python

# Imports (standard library)
import os
import sys

# Imports (3rd-party)
import dotenv
import requests

# Imports (local application)
from hanabi_client import HanabiClient
from util import printf


# Authenticate, login to the WebSocket server, and run forever.
def main():
    # Check to see if the ".env" file exists.
    # (It is located in the repository root, which is one directory above this
    # file.)
    project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    env_path = os.path.join(project_root, ".env")
    if not os.path.exists(env_path):
        printf(
            'error: the ".env" file does not exist; copy the ".env_template" file to ".env" and edit the values accordingly'
        )
        sys.exit(1)

    # Load environment variables from the ".env" file.
    dotenv.load_dotenv(env_path)

    use_localhost = os.getenv("USE_LOCALHOST", "")
    if use_localhost == "":
        printf('error: "USE_LOCALHOST" is blank in the ".env" file')
        sys.exit(1)
    if use_localhost == "true":
        use_localhost = True
    elif use_localhost == "false":
        use_localhost = False
    else:
        printf(
            'error: "USE_LOCALHOST" should be set to either "true" or "false" in the ".env" file'
        )
        sys.exit(1)

    username = os.getenv("HANABI_USERNAME", "")
    if username == "":
        printf('error: "HANABI_USERNAME" is blank in the ".env" file')
        sys.exit(1)

    password = os.getenv("HANABI_PASSWORD", "")
    if password == "":
        printf('error: "HANABI_PASSWORD" is blank in the ".env" file')
        sys.exit(1)

    # Get an authenticated cookie by POSTing to the login handler.
    if use_localhost:
        # Assume that we are not using a certificate if we are running a local
        # version of the server.
        protocol = "http"
        ws_protocol = "ws"
        host = "localhost"
    else:
        # The official site uses HTTPS.
        protocol = "https"
        ws_protocol = "wss"
        host = "hanab.live"
    path = "/login"
    # The server rejects WebSocket connections that do not specify a client
    # version. Like with the login request below, "bot" is accepted.
    ws_path = "/ws?version=bot"
    url = protocol + "://" + host + path
    ws_url = ws_protocol + "://" + host + ws_path
    printf('Authenticating to "' + url + '" with a username of "' + username + '".')
    resp = requests.post(
        url,
        {
            "username": username,
            "password": password,
            # This is normally supposed to be the version of the JavaScript
            # client, but the server will also accept "bot" as a valid version.
            "version": "bot",
        },
    )

    # Handle failed authentication and other errors.
    if resp.status_code != 200:
        printf("Authentication failed:")
        printf(resp.text)
        sys.exit(1)

    # Get the session cookie from the response. (We cannot just copy the raw
    # "Set-Cookie" header, since it contains attributes like "Path" and
    # "HttpOnly" that are not valid in a "Cookie" request header.)
    if len(resp.cookies) == 0:
        printf("Failed to find a cookie in the authentication response headers:")
        printf(resp.headers)
        sys.exit(1)
    cookie = "; ".join(name + "=" + value for name, value in resp.cookies.items())

    HanabiClient(ws_url, cookie)


if __name__ == "__main__":
    main()
