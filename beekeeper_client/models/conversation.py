from __future__ import annotations
import uuid
import inspect
import typing

from dataclasses import dataclass, field

from beekeeper_client.models.message import Message

if typing.TYPE_CHECKING:
    from beekeeper_client.client import BeekeeperClient


@dataclass
class Conversation:
    client: BeekeeperClient

    profile: str
    replied: bool
    name: str
    conversation_type: str
    modified: str
    snippet: str
    is_admin: bool
    avatar: str
    user_id: str
    folder: str
    muted_until: str
    id: int
    is_unread: bool
    messages: list = field(default_factory=list)

    @staticmethod
    def from_dict(client, data):
        """
        Creates a Conversation object from raw data returned from the Beekeeper API
        Returns:
            Conversation: result
        """
        # Convert messages from JSON objects to Message objects first
        # API docs say we can receive message objects if we pass a non-zero limit, but I never did in my tests
        if 'messages' in data and data['messages']:
            for i, message_raw in enumerate(data['messages']):
                data['messages'][i] = Message.from_dict(client=client, data=message_raw)

        ctr_args = inspect.signature(Conversation).parameters
        args = {k: v for k, v in data.items() if k in ctr_args.keys()}
        return Conversation(client=client, **args)

    async def mark_read(self, **kwargs):
        """
        Mark a conversation as read
        Returns:
            Conversation: result Conversation object
        """
        result = await self.client.post(f'/conversations/{self.id}/read', params=kwargs)
        return Conversation.from_dict(client=self.client, data=result)

    async def get_messages(self, **kwargs):
        """
        Retrieves list of messages for given conversation
        Returns:
            list[Message]: messages
        """
        result = await self.client.get(f'/conversations/{self.id}/messages', params=kwargs)
        messages = []
        for message_raw in result:
            message = Message.from_dict(client=self.client, data=message_raw)
            message.conversation = self
            messages.append(message)

        return messages

    async def send_message(self, text, message_type='regular'):
        """
        Send a message to the conversation
        TODO: add ability to send files/media
        Args:
            text (str): text to send
            message_type (str): type of message
        Returns:
            Message: created message
        """
        data = {
            'uuid': str(uuid.uuid4()),
            'text': text,
            'message_type': message_type
        }
        result = await self.client.post(f'/conversations/{self.id}/messages', data=data)
        return Message.from_dict(client=self, data=result)
