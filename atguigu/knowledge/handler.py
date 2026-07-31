from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.knowledge.providers.register import ProviderRegister
from atguigu.knowledge.responder import KnowledgeResponder


class KnowledgeHandler:

    def __init__(self,
                 knowledge_intents: dict[str, KnowledgeIntent],
                 knowledge_responder: KnowledgeResponder,
                 providers_register: ProviderRegister
                 ):
        self._knowledge_intents = knowledge_intents
        self._knowledge_responder = knowledge_responder
        self._providers_register = providers_register

    async def handle(self,
                     state: DialogueState,
                     intents: list[str]) -> list[BotMessage]:
        pass

        # 1. 根据LLM提供的知识意图的id(intent),找提供者ID(provider_id)

        # 2. 根据提供者ID，查询提供这对象(Provider)

        # 3. 调用提供者的检索方法 获取到各个提供者提供的内容

        # 4. 将从所有提供者查询获取到的结果给responder组件用
