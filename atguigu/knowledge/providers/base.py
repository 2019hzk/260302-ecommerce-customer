from abc import ABC, abstractmethod
from dataclasses import  dataclass
from atguigu.domain.state import DialogueState



@dataclass(slots=True)
class KnowledgeChunk:
    content: str


class Provider(ABC):
    """
    抽象基类
    """

    provider_id: str

    @abstractmethod
    async def retrival(self,
                       state: DialogueState)->list[KnowledgeChunk]:
        pass
