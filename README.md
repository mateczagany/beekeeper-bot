# Beekeeper Bot
Example bot application to use with Beekeper, still WIP

I couldn't find any way to get incoming messages real-time so the application will poll all conversation at a pre-configured rate.

Please see a very simple example in [main.py](/main.py) - `callback_test()` will be called on every message the bot receives and it will also send back a message. 

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