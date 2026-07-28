from typing import Any

from atguigu.task.action.base import Action, ActionResult


class ActionResponse(Action):
    name = "action_response"

    async def run(self, action_kwargs: dict[str, Any]) -> ActionResult:

        pass


