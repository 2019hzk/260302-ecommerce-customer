from pathlib import Path

from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.validator import TurnPlanValidator
from atguigu.clarify.responder import ClarifyResponder
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.flows.executor import FlowExecutor
from atguigu.task.handler import TaskHandler
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.chitchat.handler import ChitChatHandler
from atguigu.task.flows.loader import FlowLoader
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]

FLOW_CONFIG_DIR = PROJECT_ROOT_DIR / "flow_config"

FLOW_CONFIGS = ["system_flows.yml", "user_flows.yml"]


def build_dialogue_engine():
    flows_list = FlowLoader().load_multi_yaml([FLOW_CONFIG_DIR / flow_config for flow_config in FLOW_CONFIGS])

    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_plan_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponder(),
        task_handler=TaskHandler(
            flows_list=flows_list,
            command_processor=CommandProcessor(),
            flow_executor=FlowExecutor()
        ),
        knowledge_handler=KnowledgeHandler(intents=KNOWLEDGE_INTENTS),
        chitchat_handler=ChitChatHandler()
    )
