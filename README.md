# Beekeeper Bot
Example bot application to use with Beekeper, still WIP

The application uses the official PubNub library to get real-time events about messages. You won't find `BeekeeperBotMessageDecrypter` class in this repository as I'm not sure if I'm allowed to publish the logic here.

Please see a very simple example in [main.py](/main.py) - `callback_test()` will be called on every message the bot receives and it will also send back a message.
 
TODO: 
- PubNub async support is limited, message callbacks are always called as sync functions, find a solution for this
- models (e.g. Message and Conversation classes) could be generated from online documentation   


## Requirements:
- Python 3.7
- pip

## Installation
```
cp config.example.yml config.yml
vi config.yml
pip install -r requirements.txt
python main.py
```