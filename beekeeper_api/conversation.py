from __future__ import annotations
import uuid
import inspect
import typing

from dataclasses import dataclass

from beekeeper_api.message import Message

if typing.TYPE_CHECKING:
    from beekeeper_api.client import BeekeeperClient


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

    @staticmethod
    def from_dict(client, data):
        """
        Creates a Conversation object from raw data returned from the Beekeeper API
        Returns:
            Conversation: result
        """
        ctr_args = inspect.signature(Conversation).parameters
        args = {k: v for k, v in data.items() if k in ctr_args.keys()}
        return Conversation(client=client, **args)

    async def get_messages(self, **kwargs):
        """
        Retrieves list of messages for given conversation
        Returns:
            list[Message]: messages
        """
        result = await self.client.get(f'/conversations/{self.id}/messages', params=kwargs)
        return [Message.from_dict(client=self.client, data=message_raw) for message_raw in result]

    async def send_message(self, text, message_type):
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
