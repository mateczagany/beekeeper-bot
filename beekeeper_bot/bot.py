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
    def __init__(self, beekeeper_client):
        """
        Args:
            beekeeper_client (BeekeeperClient): client
        """
        self._client = beekeeper_client

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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return

    def on_message(self, message):
        """
        Called by the message listener when there is a new message, this function will call callbacks as well
        Args:
            message (Message): new message
        Returns:
            None
        """
        for cb in self._callbacks:
            cb(self, message)

    def get_client(self):
        """
        Returns:
            BeekeeperClient: beekeeper client object
        """

    def add_callback(self, callback):
        """
        Adds a callback for when a message arrives
        Args:
            callback (func): callback function to call
        Returns:
            None
        """
        self._callbacks.append(callback)

    async def start(self):
        """
        Sets up PubNub listener to given conversation so we get real-time notifications of messages
        This will run until stop() is called
        Returns:
            None
        """
        message_decrypter = BeekeeperBotMessageDecrypter(base64.b64decode(self._pubnub_channel_key))

        message_listener = BeekeeperBotMessageListener(bot=self, decrypter=message_decrypter)

        pubnub_config = PNConfiguration()
        pubnub_config.subscribe_key = self._pubnub_key
        pubnub_config.reconnect_policy = PNReconnectionPolicy.LINEAR
        pubnub_config.connect_timeout = 30

        pubnub = PubNubAsyncio(config=pubnub_config)
        pubnub.add_listener(message_listener)
        pubnub.subscribe().channels([self._pubnub_channel_name]).execute()

        self._is_running = True

        while True:
            await asyncio.sleep(.2)
            if not self._is_running:
                pubnub.unsubscribe_all()
                pubnub.stop()
                break

    def stop(self):
        """
        Stop polling messages
        Returns:
            None
        """
        self._is_running = False

    def is_running(self):
        """
        Is the bot running?
        Returns:
            bool: is it running
        """
        return self._is_running
