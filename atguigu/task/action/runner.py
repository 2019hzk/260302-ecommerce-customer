from typing import Any
from dataclasses import dataclass, field

from atguigu.task.action.base import ActionResult
from atguigu.task.action.register import ActionRegister


@dataclass(slots=True)
class ActionCall:
    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)


class ActionRunner:
    """
    专门负责运行Action
    ActionRegister---找到action---运行action[执行action的run方法]
    """

    def __init__(self, action_register: ActionRegister):
        self.action_register = action_register

    async def run(self, action_call: ActionCall) -> ActionResult:
        # 1. 获取action对象
        action = self.action_register.get_action(action_call.action_name)

        # 2. 执行action
        action_result = action.run(action_call.action_kwargs)

        return action_result
