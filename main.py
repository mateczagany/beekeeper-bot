import logging
import asyncio
import yaml

from beekeeper_api.client_settings import BeekeeperClientSettings
from beekeeper_api.client import BeekeeperClient
from beekeeper_bot.bot import BeekeeperBot
from beekeeper_bot.bot_settings import BeekeeperBotSettings

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting bot...")

    with open('config.yml', 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.BaseLoader)

    client_settings = BeekeeperClientSettings(
        subdomain=config['beekeeper_client']['subdomain'],
        api_version=config['beekeeper_client']['version'],
        access_token=config['beekeeper_client']['access_token']
    )

    bot_settings = BeekeeperBotSettings(
        poll_rate=config['beekeeper_bot']['poll_rate']
    )

    async with BeekeeperClient(client_settings=client_settings) as client:
        async with BeekeeperBot(bot_settings=bot_settings, beekeeper_client=client) as bot:
            print(bot)

    logger.info("Bot has shut down")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
