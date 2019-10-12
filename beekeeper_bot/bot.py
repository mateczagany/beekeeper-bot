import asyncio
import logging
from datetime import timedelta

from beekeeper_api.client import BeekeeperClient
from beekeeper_api.conversation import Conversation
from beekeeper_api.message import Message
from beekeeper_api.util import bkdt_to_dt, dt_to_bkdt
from beekeeper_bot.bot_settings import BeekeeperBotSettings

logger = logging.getLogger(__name__)


class BeekeeperBot:
    def __init__(self, bot_settings, beekeeper_client):
        """
        Args:
            bot_settings (BeekeeperBotSettings): bot settings
            beekeeper_client (BeekeeperClient): client
        """
        self.bot_settings = bot_settings
        self.client = beekeeper_client

        self.should_exit = False
        self.callbacks = []
        self.conversation_data = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return

    async def _on_message(self, message):
        """
        Called internally when there is a new message, this function will call callbacks as well
        Args:
            message (Message): new message
        Returns:
            None
        """
        for cb in self.callbacks:
            await cb(self, message)

    async def _poll_conversation(self, conv):
        """
        Get new messages from given conversation
        Args:
            conv (Conversation): conversation object
        Returns:
            None
        """
        # is_unread wasn't always properly set for me, so I'm looking at `modified` here to see if we received new msg
        # even though we will also process messages that were sent by us, the bot doesn't miss any messages this way
        if bkdt_to_dt(conv.modified) == self.conversation_data[conv.id]['last_modified']:
            return

        logger.debug(f'Got unread message in {conv.name}, snippet: {conv.snippet}')

        if conv.id in self.conversation_data:
            after_date = self.conversation_data[conv.id]['last_modified'] - timedelta(seconds=1)
            messages = await conv.get_messages(after=dt_to_bkdt(after_date))

            self.conversation_data[conv.id]['last_modified'] = bkdt_to_dt(conv.modified)
        else:
            messages = await conv.get_messages()
            self.conversation_data[conv.id] = {
                'last_modified': bkdt_to_dt(conv.modified),
                'messages_read': set()
            }

        if not messages:
            logger.warning(f'No messages for conversation {conv.name} even though it was marked as unread')
            return

        for message in messages:
            if message.sent_by_user:
                continue

            if message.id in self.conversation_data[conv.id]['messages_read']:
                continue

            self.conversation_data[conv.id]['messages_read'].add(message.id)

            await self._on_message(message)

        await conv.mark_read()

    async def _poll_messages(self):
        """
        Called at every X seconds to poll all conversations
        Returns:
            None
        """
        conversations = await self.client.get_conversations()
        futures = [self._poll_conversation(conv) for conv in conversations]
        await asyncio.gather(*futures)

    def add_callback(self, callback):
        """
        Adds a callback for when a message arrives
        Args:
            callback (func): callback function to call
        Returns:
            None
        """
        self.callbacks.append(callback)

    async def start(self):
        """
        Start polling messages, will only stop after stop() is called
        Returns:
            None
        """
        # First mark all messages read, we only need to read the last message for this
        # We may want to get rid of this in the future to process messages that were sent while the bot was offline
        futures = []
        for conv in await self.client.get_conversations():
            messages = await conv.get_messages(limit=1)
            if messages:
                self.conversation_data[conv.id] = {
                    'last_modified': bkdt_to_dt(conv.modified),
                    'messages_read': set()
                }
                futures.append(messages[0].mark_read())

            await conv.mark_read()

        await asyncio.gather(*futures)

        self.should_exit = False
        while not self.should_exit:
            await self._poll_messages()
            await asyncio.sleep(self.bot_settings.poll_rate)

    async def stop(self):
        """
        Stop polling messages
        Returns:
            None
        """
        self.should_exit = True
