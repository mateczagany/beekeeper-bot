import logging
import asyncio
import sys

import yaml

from beekeeper_api.client_settings import BeekeeperClientSettings
from beekeeper_api.client import BeekeeperClient
from beekeeper_api.message import Message
from beekeeper_bot.bot import BeekeeperBot
from beekeeper_bot.bot_settings import BeekeeperBotSettings


# TODO: better logging
console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s :: %(name)s :: %(message)s'))

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)

logging.getLogger('asyncio').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def callback_test(bot, message):
    """
    Args:
        bot (BeekeeperBot):  bot
        message (Message): message object
    """
    logger.info(f"Got message from {message.profile} at {message.created}: {message.text}")
    await message.conversation.send_message(f'I got your message: {message.text}')


async def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.BaseLoader)

    client_settings = BeekeeperClientSettings(
        subdomain=config['beekeeper_client']['subdomain'],
        api_version=config['beekeeper_client']['version'],
        access_token=config['beekeeper_client']['access_token']
    )

    bot_settings = BeekeeperBotSettings(
        poll_rate=int(config['beekeeper_bot']['poll_rate'])
    )

    async with BeekeeperClient(client_settings=client_settings) as client:
        async with BeekeeperBot(bot_settings=bot_settings, beekeeper_client=client) as bot:
            bot.add_callback(callback=callback_test)
            try:
                await asyncio.wait_for(bot.start(), 60)  # run for 60 seconds only
            except asyncio.TimeoutError:
                logger.info("Shutting down bot")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
