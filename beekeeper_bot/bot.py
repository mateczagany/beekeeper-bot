from beekeeper_api.client import BeekeeperClient


class BeekeeperBot:
    def __init__(self, bot_settings, beekeeper_client):
        """
        Args:
            bot_settings: (BotSettings):
            beekeeper_client (BeekeeperClient): client
        """
        self.bot_settings = bot_settings
        self.client = beekeeper_client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return

    def _poll(self):
        """
        Called at every X seconds
        Returns:
            None
        """
        pass
