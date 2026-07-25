from typing import Any
from dataclasses import dataclass

from atguigu.task.command.commands import Command

"""
任务：
任务的输入：
约束：
1.
2.
3.
4. 输出结构（json格式字符串）---->【字典----对象】
"""


@dataclass(slots=True)
class TaskTurnPlan:
    commands: list[Command]  # 具体的类型

    @classmethod
    def from_dict(cls, task_data: dict[str, Any]) -> "TaskTurnPlan":
        return cls(
            commands=[Command.from_dict(command_dict) for command_dict in task_data['commands']]
        )


@dataclass(slots=True)
class KnowledgeTurnPlan:
    intents: list[str]

    @classmethod
    def from_dict(cls, knowledge_data: dict[str, Any]) -> "KnowledgeTurnPlan":
        return cls(
            intents=knowledge_data['intents']
        )


@dataclass(slots=True)
class ChitChatTurnPlan:
    chat: str

    @classmethod
    def from_dict(cls, chat_data: dict[str, Any]) -> "ChitChatTurnPlan":
        return cls(
            chat=chat_data['chat']
        )


@dataclass(slots=True)
class TurnPlan:
    """
    数据模型
    作用：一轮的路由结果
    """
    task: TaskTurnPlan | None = None  # 业务流程任务轨道
    knowledge: KnowledgeTurnPlan | None = None  # 知识检索轨道
    chitchat: ChitChatTurnPlan | None = None  # 闲聊轨道

    @classmethod
    def from_dict(cls, turn_plan_data: dict[str, Any]) -> "TurnPlan":
        return cls(
            task=TaskTurnPlan.from_dict(turn_plan_data['task']) if turn_plan_data.get('task') is not None else None,
            knowledge=KnowledgeTurnPlan.from_dict(turn_plan_data['knowledge']) if turn_plan_data.get(
                'knowledge') is not None else None,
            chitchat=ChitChatTurnPlan.from_dict(turn_plan_data['chitchat']) if turn_plan_data.get(
                'chitchat') is not None else None
        )
