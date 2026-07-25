
from atguigu.engine.dialogue_engine import  DialogueEngine
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.validator import TurnPlanValidator
from atguigu.clarify.responder import ClarifyResponder
from atguigu.task.handler import TaskHandler
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.chitchat.handler import ChitChatHandler


def  build_dialogue_engine():

    return  DialogueEngine(
        turn_planner= TurnPlanner(),
        turn_plan_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponder(),
        task_handler=TaskHandler(),
        knowledge_handler=KnowledgeHandler(),
        chitchat_handler=ChitChatHandler()
    )


