import logging
import asyncio
import sys

import yaml

from beekeeper_client.client_settings import BeekeeperClientSettings
from beekeeper_client.client import BeekeeperClient
from beekeeper_client.models.message import Message
from beekeeper_bot.bot import BeekeeperBot


# TODO: better logging
console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s :: %(name)s :: %(message)s'))

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)

logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('pubnub').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def callback_test(bot, message):
    """
    Args:
        bot (BeekeeperBot):  bot
        message (Message): message object
    """
    if message.sent_by_user:
        return

    logger.info(f"Got message from {message.profile} at {message.created}: {message.text}")
    conversation = await message.get_conversation()
    await conversation.send_message(f'I got your message: {message.text}')


async def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.BaseLoader)

    client_settings = BeekeeperClientSettings(
        subdomain=config['beekeeper_client']['subdomain'],
        access_token=config['beekeeper_client']['access_token']
    )

    async with BeekeeperClient(client_settings=client_settings) as client:
        async with BeekeeperBot(beekeeper_client=client, event_loop=asyncio.get_event_loop()) as bot:
            bot.add_callback(callback=callback_test)
            bot_task = asyncio.ensure_future(bot.start())

            # if bot didn't exit in given timeout, then cancel it
            await asyncio.wait([bot_task, asyncio.sleep(600)], return_when=asyncio.FIRST_COMPLETED)

            if bot.is_running():
                logger.info("Bot shutting down...")
                bot.stop()

            await bot_task

            logger.info("Bot has shut down")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
