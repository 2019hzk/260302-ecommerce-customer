import uuid
from dataclasses import dataclass
from fastapi import APIRouter

from atguigu.api.schemas import ChatRequest, ChatResponse, ChatBotMessage, ChatObject
from atguigu.domain.messages import UserMessage, ProcessResult, MessageType, FocusedObject
from atguigu.api.dependencies import DialogueServiceDep
router = APIRouter()


@dataclass
class User:
    name: str
    age: int
    address: str


@router.get("/hello", response_model=User)
def hello():
    """
    路由函数返回的数据模型自动会被fastapi(springmvc[springboot])进行序列化
    响应：User对象-----fastapi-----"{}" json格式的字符串：是个字符串  "abc"
    请求：前端发送请求（请求数据）---->请求体中(application/json)---json格式的字符串--- fastapi-----对象（定义这个对象） 反序列化
    "{"name":"zs","age":18,"address":"sz"}"----User
    :return:

    指定response_model之后
    1. 可以通过swagger_ui 看到接口的详细响应信息，不只是有状态嘛，还有schema约束（响应字段、字段类型）
    2. 过滤字段
    3. 字段类型校验以及类型转换
    4. 序列化(加不加都能序列化)
    """
    return {
        "name": "zs",
        "age": "abc",
        "address": "sz",
    }


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest,
                        service: DialogueServiceDep):
    """
    :param chat_request:
    :return:
    """
    # 1. 接口数据模型转换成领域数据模型
    user_message = _build_user_message(chat_request)

    # 2. 调用service处理消息（领域数据模型）--- 结果：领域数据模型
    process_result: ProcessResult = await service.process_message(user_message)

    # 3. 将结果领域数据模型转换成接口数据模型
    chat_response = _build_chat_response(process_result)

    # 4. 返回接口数据模型
    return chat_response


def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    return UserMessage(
        sender_id=chat_request.sender_id,
        message_id=str(uuid.uuid4()),
        type=MessageType.OBJECT if chat_request.object is not None else MessageType.TEXT,
        text=chat_request.text,
        object=FocusedObject(
            id=chat_request.object.id,
            type=chat_request.object.type,
            title=chat_request.object.title,
            attributes=chat_request.object.attributes
        ) if chat_request.object is not None else None
    )


def _build_chat_response(process_result: ProcessResult) -> ChatResponse:
    return ChatResponse(
        message_id=process_result.message_id,
        messages=[
            ChatBotMessage(text=bot_message.text,
                           object=ChatObject(
                               id=bot_message.object.id,
                               type=bot_message.object.type,
                               title=bot_message.object.title,
                               attributes=bot_message.object.attributes
                           ) if bot_message.object is not None else None
                           )
            for bot_message in process_result.messages
        ]
    )
