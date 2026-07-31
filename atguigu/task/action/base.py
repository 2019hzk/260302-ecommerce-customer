from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState


@dataclass(slots=True)
class ActionResult:
    messages: list[BotMessage] = field(default_factory=list)  # action_response的run方法一定会给messages内容 但是下面三个action_xxx不一定
    slots: dict[str, Any] = field(default_factory=dict)  # action_xxx的run方法一定会给slots


class Action(ABC):
    """
    抽象基类
    """

    name: str

    @abstractmethod
    async def run(self,
                  action_kwargs: dict[str, Any],
                  state:DialogueState,
                  ) -> ActionResult:
        pass
