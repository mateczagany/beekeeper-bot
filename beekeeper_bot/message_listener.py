import json
import logging

from pubnub.pubnub_asyncio import PubNubAsyncio
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.models.consumer.common import PNStatus
from pubnub.models.consumer.pubsub import PNPresenceEventResult
from pubnub.models.consumer.signal import PNSignalResult

from beekeeper_bot.exceptions import BeekeeperBotException
from beekeeper_client.models.message import Message

logger = logging.getLogger(__name__)


class BeekeeperBotMessageListener(SubscribeCallback):
    def __init__(self, bot, decrypter):
        """
        Args:
            bot (BeekeeperBot): Beekeeper bot object
            decrypter (MessageDecrypter): message decrypter to use when we get a message
        """
        self._bot = bot
        self._message_decrypter = decrypter
        super().__init__()

    def status(self, pubnub, status):
        """
        Args:
            pubnub (PubNubAsyncio): PubNub object
            status (PNStatus): status object
        """
        if not status:
            return

        if status.category in (PNStatusCategory.PNConnectedCategory, PNStatusCategory.PNReconnectedCategory):
            logger.info("PubNub listener successfully connected")
            return

        if status.category != PNStatusCategory.PNAcknowledgmentCategory:
            raise BeekeeperBotException(f"Status error, category: {status.category}, "
                                        f"error: {status.error}, error data: {status.error_data}")

    def presence(self, pubnub, presence):
        """
        Args:
            pubnub (PubNubAsyncio): PubNub object
            presence (PNPresenceEventResult): presence event object
        """
        pass

    def message(self, pubnub, msg_encrypted):
        """
        Args:
            pubnub (PubNubAsyncio): PubNub object
            msg_encrypted (PNMessageResult): message object
        """
        msg_decrypted = self._message_decrypter.decode(msg_encrypted.message)
        if not msg_decrypted:
            return

        msg_json = json.loads(msg_decrypted)
        if 'type' not in msg_json or msg_json['type'] != 'message':
            return

        msg = Message.from_dict(client=self._bot.get_client(), data=msg_json['data'])
        self._bot.on_message(msg)

    def signal(self, pubnub, signal):
        """
        Args:
            pubnub (PubNubAsyncio): PubNub object
            signal (PNSignalResult): signal object
        """
        pass
