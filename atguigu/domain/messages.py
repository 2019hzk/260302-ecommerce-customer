"""
封装两种角色的消息
User:用户的角色
Bot:机器人角色

IO /网络传输 不能直接读写对象或者发送对象以及接收对象
对象只在内存中有
"""
from enum import Enum
from typing import Any, Self
from dataclasses import field, dataclass


class MessageType(Enum):
    TEXT = "text"
    OBJECT = "object"


@dataclass(slots=True)  # 1. 提高访问速度 2.空间占用的更少   3.属性个数固定
class FocusedObject:
    id: str  # 订单编号 or 商品号
    type: str  # "order" or "product"
    title: str
    attributes: dict[str, Any] = field(default_factory=dict)  # 订单的属性or商品属性

    def to_dict(self) -> dict[str, Any]:
        """
        数据库写(次操作字符串更加方便)
        :return:
        """
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "attributes": dict(self.attributes)  # 浅拷贝 数据更加安全
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:  # 返回类本身
        """
        应用代码使用（操作对象）
        :param data:
        :return:
        """
        return cls(
            id=data['id'],
            type=data['type'],
            title=data['title'],
            attributes=dict(data['attributes'])
        )


@dataclass(slots=True)
class UserMessage:
    sender_id: str  # 发消息的用户ID 必填字段
    message_id: str  # 消息ID(自己赋值)
    type: MessageType  # 消息类型
    text: str | None = None  # 文本消息内容
    object: FocusedObject | None = None  # 对象消息的内容

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "type": self.type.value,
            "text": self.text,
            "object": FocusedObject.to_dict(self.object) if self.object is not None else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserMessage":
        object_data = data['object']
        return cls(
            sender_id=data['sender_id'],
            message_id=data['message_id'],
            type=MessageType(data['type']),
            text=data['text'],
            object=FocusedObject.from_dict(object_data) if object_data is not None else None
        )


@dataclass(slots=True)
class BotMessage:
    text: str  # 当下承载机器人的回复（文本内容） 一定会有值
    object: FocusedObject | None = None  # 承载机器人的回复对象（后续内容扩展） TODO

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "object": FocusedObject.to_dict(self.object) if self.object is not None else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BotMessage":
        object_data = data['object']
        return cls(
            text=data['text'],
            object=FocusedObject.from_dict(object_data) if object_data is not None else None
        )



