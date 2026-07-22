
"""
接口数据模型：前后端交互使用
"""


from typing import Any

from pydantic import  BaseModel,Field

class ChatObject(BaseModel):
    id: str
    type: str
    title: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class ChatBotMessage(BaseModel):
    text: str
    object: ChatObject | None = None



class   ChatRequest(BaseModel):
    """
    请求数据模型
    """
    sender_id:str
    message_id:str
    text: str  |None =None
    object: ChatObject | None=None


class ChatResponse(BaseModel):
    """
    响应数据模型
    """
    message_id:str
    messages:list[ChatBotMessage]








