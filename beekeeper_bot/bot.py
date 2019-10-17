import asyncio
import base64
import logging

from pubnub.enums import PNReconnectionPolicy
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_asyncio import PubNubAsyncio

from beekeeper_bot.message_decrypter import BeekeeperBotMessageDecrypter
from beekeeper_bot.message_listener import BeekeeperBotMessageListener
from beekeeper_client.client import BeekeeperClient
from beekeeper_client.models.message import Message
from beekeeper_bot.exceptions import BeekeeperBotException

logger = logging.getLogger(__name__)


class BeekeeperBot:
    def __init__(self, beekeeper_client, event_loop):
        """
        Args:
            beekeeper_client (BeekeeperClient): client
            event_loop
        """
        self._client = beekeeper_client
        self._event_loop = event_loop or asyncio.get_event_loop()

        self._pubnub = None
        self._is_running = False
        self._callbacks = []
        self.conversation_data = {}

        try:
            self._pubnub_key = self._client.user_config['tenant']['integrations']['pubnub']['subscribe_key']
            self._pubnub_channel_name = self._client.user_config['enc_channel']['channel']
            self._pubnub_channel_key = self._client.user_config['enc_channel']['key']
        except KeyError:
            raise BeekeeperBotException('Failed to retrieve PubNub settings')

    async def __aenter__(self):
        message_decrypter = BeekeeperBotMessageDecrypter(base64.b64decode(self._pubnub_channel_key))
        message_listener = BeekeeperBotMessageListener(bot=self, decrypter=message_decrypter)

        pubnub_config = PNConfiguration()
        pubnub_config.subscribe_key = self._pubnub_key
        pubnub_config.reconnect_policy = PNReconnectionPolicy.LINEAR
        pubnub_config.connect_timeout = 30

        self._pubnub = PubNubAsyncio(config=pubnub_config)
        self._pubnub.add_listener(message_listener)
        self._pubnub.subscribe().channels([self._pubnub_channel_name]).execute()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._pubnub.unsubscribe_all()
        self._pubnub.stop()

    def on_message(self, message):
        """
        Called by the message listener when there is a new message, this function will call callbacks as well
        Args:
            message (Message): new message
        Returns:
            None
        """
        futures = [cb(self, message) for cb in self._callbacks]
        asyncio.ensure_future(*futures, loop=self._event_loop)

    def get_client(self):
        """
        Returns:
            BeekeeperClient: beekeeper client object
        """
        return self._client

    def add_callback(self, callback):
        """
        Adds a callback for when a message arrives
        Args:
            callback (func): callback function to call
        Returns:
            None
        """
        self._callbacks.append(callback)
