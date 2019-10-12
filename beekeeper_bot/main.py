import logging
import asyncio

from beekeeper_bot.client.api_settings import BeekeeperClientSettings
from beekeeper_bot.client.beekeeper_client import BeekeeperClient
from beekeeper_bot.config import CONFIG

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting bot...")

    api_settings = BeekeeperClientSettings(
        subdomain=CONFIG['beekeeper_api']['subdomain'],
        api_version=CONFIG['beekeeper_api']['vversion'],
        access_token=CONFIG['beekeeper_api']['access_token']
    )
    async with BeekeeperClient(api_settings=api_settings) as client:
        conversations = await client.get_conversations()

        for conv in conversations:
            if conv.profile == CONFIG['beekeeper_api']['subdomain']:
                continue  # this guy is there by default, don't mind him

            print([c.text for c in await conv.get_messages()])
            await conv.send_message(text='Hello there', message_type='regular')

    logger.info("Bot has shut down")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
