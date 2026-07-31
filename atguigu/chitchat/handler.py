from atguigu.chitchat.responder import ChitChatResponder
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState


class ChitChatHandler:

    def __init__(self, chat_responder: ChitChatResponder):
        self._chat_responder = chat_responder

    async def handle(self,
                     chitchat: str,
                     state: DialogueState) -> list[BotMessage]:
        return await self._chat_responder.respond_chat(chitchat, state)
