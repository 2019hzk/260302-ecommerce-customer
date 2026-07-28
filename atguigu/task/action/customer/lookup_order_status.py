from typing import Any

from atguigu.task.action.base import Action, ActionResult


class ActionLookupOrderStatus(Action):

    name = "action_lookup_order_status"

    async def run(self, action_args: dict[str, Any]) -> ActionResult:
        pass

