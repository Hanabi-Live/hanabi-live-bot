# hanabi-live-bot

<!-- markdownlint-disable MD033 -->

An example reference bot for the [Hanab Live website](https://github.com/Zamiell/hanabi-live) written in [Python 3](https://www.python.org/).

<br>

## Setup Instructions

- Clone the repository:
  - `git clone git@github.com:Hanabi-Live/hanabi-live-bot.git`
  - `cd hanabi-live-bot`
- Install the dependencies:
  - `pip install -r requirements.txt`
- Set up environment variables:
  - `cp .env_template .env`
  - `vim .env`
- Run it:
  - `python src/main.py`
- In a browser, log on to the website and start a new table.
- In the pre-game chat window, send a private message to the bot in order to get it to join you:
  - `/msg [username] /join`
- Then, start the game and play!
