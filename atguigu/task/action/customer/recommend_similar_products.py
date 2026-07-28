from typing import Any

from atguigu.task.action.base import Action, ActionResult


class ActionRecommendSimilarProducts(Action):
    name = "action_recommend_similar_products"

    async def run(self, action_args: dict[str, Any]) -> ActionResult:
        pass
