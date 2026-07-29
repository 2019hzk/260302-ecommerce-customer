from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.customer.shared import  fetch_logistics


class ActionLookUpLogistic(Action):
    name = "action_lookup_logistics"

    async def run(self, action_args: dict[str, Any], state: DialogueState) -> ActionResult:
        order_number = state.activated_task.slots.get("order_number")
        payload = await fetch_logistics(order_number)

        if payload is None:
            return ActionResult(slots={
                "tracking_number": "未知",
                "logistics_company": "未知",
                "logistics_status": "暂时无法查到物流信息，请稍后再试。",
            })

        return ActionResult(slots={
            "tracking_number": payload.get("tracking_number") or "未知",
            "logistics_company": payload.get("logistics_company") or "未知",
            "logistics_status": payload.get("status_desc") or payload.get("status") or "未知",
        })