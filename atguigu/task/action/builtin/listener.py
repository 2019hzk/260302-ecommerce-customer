from typing import Any

from atguigu.task.action.base import Action, ActionResult


class ActionListener(Action):
    name = "action_listen"

    async def run(self, action_args: dict[str, Any]) -> ActionResult:
        pass


