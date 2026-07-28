from typing import Any

from atguigu.task.action.base import Action, ActionResult


class ActionLookUpLogistic(Action):

    name = "action_lookup_logistics"

    async def run(self, action_args: dict[str, Any]) -> ActionResult:
        pass

