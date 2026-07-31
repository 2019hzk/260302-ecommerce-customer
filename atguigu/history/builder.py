from typing import Literal

from atguigu.domain.messages import UserMessage, BotMessage, MessageType, FocusedObject, ChatHistoryMessage
from atguigu.domain.state import Turn


class ChatHistoryBuilder:

    @staticmethod
    def build(turns: list[Turn]) -> str:
        """
        构建历史对话(后10轮)
        Q: 用户问题
        A: 机器人回复
        Returns:
            “
            Q:
            A:
            Q:
            A:
            ....
            ”

        """
        chat_history = []
        for turn in turns:
            # 1. 获取用户角色的消息(Q)
            user_message = turn.user_message
            user_message_str = ChatHistoryBuilder.build_user_message(user_message)
            chat_history.append(f"USER: {user_message_str}")

            # 2. 获取机器人角色的消息(A)
            bot_messages = turn.bot_messages
            for bot_message in bot_messages:
                bot_message_str = ChatHistoryBuilder._build_bot_message(bot_message)
                chat_history.append(f"BOT: {bot_message_str}")

        return "\n".join(chat_history)

    @staticmethod
    def build_user_message(user_message: UserMessage) -> str:
        """
        构建用户角色消息的str
        Args:
            user_message:

        Returns:
            str

        """
        if user_message.type is MessageType.TEXT:
            return ChatHistoryBuilder._render_text_message(user_message.text)

        return ChatHistoryBuilder._render_object_message(user_message.object)

    @staticmethod
    def _build_bot_message(bot_message: BotMessage) -> str:
        """
        构建机器人角色消息的str
        Args:
            bot_message:
        Returns:
        """
        if bot_message.text:
            return ChatHistoryBuilder._render_text_message(bot_message.text)

        return ChatHistoryBuilder._render_object_message(bot_message.object)

    @classmethod
    def _render_text_message(cls, text: str) -> str:
        return text.strip()

    @classmethod
    def _render_object_message(cls, object: FocusedObject) -> str:
        """
        id:
        type:
        title:
        attributes:
        Args:
            object:

        Returns:
            str

        """
        id = object.id
        label = "订单" if object.type == "order" else "商品"
        title = object.title
        attributes_str = "|".join([f"{k}={v}" for k, v in object.attributes.items()])

        return f"【id={id} label={label} title={title} attributes={attributes_str}】"

    @classmethod
    def build_chat_history(cls,
                           session_id: str,
                           role: Literal["user", "bot"],
                           text: str,
                           object: FocusedObject) -> ChatHistoryMessage:

        return ChatHistoryMessage(session_id=session_id,
                                  role=role,
                                  text=text,
                                  object=object
                                  )
