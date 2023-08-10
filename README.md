# hanabi-live-bot

An example reference bot for the [Hanab Live website](https://github.com/Zamiell/hanabi-live) written in [Python 3](https://www.python.org/).

<br />

### Setup Instructions

* Install the dependencies:
  * `pip install -r requirements.txt`
* Set up environment variables:
  * `cp .env_template .env`
  * `vim .env`
* Run it:
  * `python main.py {username}`
* In a browser, log on to the website and start a new table.
* In the pre-game chat window, send a private message to the bot in order to get it to join you:
  * `/msg {username} /join`
* Or accomplish the same via the command line:
  * `python main.py {username} {user_to_join}`
* Alternatively, you can get the bot to create a table:
  * `python main.py {username} create`
* Optionally have the bot set the variant:
  * `/msg {username} /setvariant {var_name}`
  * Special substrings must be substituted: ` & ` must be replaced with `+`, and spaces replaced with `_`.
  * There are shorthands to choose the number of suits as well: `3s,4s,5s,6s` for `(3 Suits), ..., (6 Suits)`.
  * Example: `/msg {username} /setvariant Black+Rainbow_5s`
* Then, start the game and play!
  * `/msg {username} /start`
