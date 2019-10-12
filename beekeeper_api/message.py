from __future__ import annotations
import inspect
import typing

from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from beekeeper_api.client import BeekeeperClient
    from beekeeper_api.conversation import Conversation


@dataclass
class Message:
    client: BeekeeperClient

    profile: str
    user_id: str
    name: str
    created: str
    text: str
    message_type: str
    avatar: str
    conversation_id: str
    sent_by_user: bool
    id: int
    uuid: str

    current_receipt_state: str  # it's not actually in Beekeeper docs? it might be useful for the bot though

    conversation: Conversation = None

    @staticmethod
    def from_dict(client, data):
        """
        Creates a Message object from raw data returned from the Beekeeper API
        Returns:
            Message: result
        """
        ctr_args = inspect.signature(Message).parameters
        args = {k: v for k, v in data.items() if k in ctr_args.keys()}
        return Message(client=client, **args)

    async def mark_read(self):
        """
        Marks all messages up to this message as read
        Returns:
            None
        """
        await self.client.post(f'/conversations/{self.conversation_id}/messages/{self.id}/read')
