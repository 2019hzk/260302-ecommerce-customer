"""
定义YAML中流程的边
YAML---加载成字典-->对象（from_dict）方法
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any

from atguigu.task.flows.links import FlowStepLink, FlowStepStaticLink, FlowStepConditionLink, FlowStepFallbackLink


@dataclass(slots=True)
class ResponseDefinition:
    text: str  # 定义要说的话 【LLM定义要说的话】
    mode: str = "static"  # 开关   【static:自己定义的话   generate:llm 重0生成【只有提示词，没有模版】   rephrase:llm：基于模版（text）改写生成【提示词】】
    prompt: str | None = None


@dataclass(slots=True)
class SlotValidate:
    condition: str
    failure_response: ResponseDefinition | None = None  # 不填错误信息 自己内置标准的错误信息


class FLowStepType(Enum):
    START = "start"
    END = "end"
    ACTION = "action"
    COLLECT = "collect"


@dataclass(slots=True)
class FlowStep:
    """
    流程步骤基类
    """
    id: str
    type: FLowStepType
    next: list[FlowStepLink]

    @staticmethod
    def from_dict(step_data: dict[str, Any]) -> "FlowStep":
        """
        data: dict[str,Any]
        Args:
            step_data:  某一个业务流程的步骤字典对象

        Returns:

        """
        flow_step_type = step_data['type']
        clz = FLOW_STEP_TO_CLASS[flow_step_type]
        return clz.from_dict(step_data)

    @staticmethod
    def _load_base_fields(step_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": step_data['id'],
            "type": FLowStepType(step_data['type']),
            "next": FlowStep._load_step_links(step_data['next'])

        }

    @staticmethod
    def _load_step_links(link_data: str | list[dict[str, Any]]) -> list[FlowStepLink]:
        links: list[FlowStepLink] = []
        # 1. 顺序边
        if isinstance(link_data, str):
            links.append(FlowStepStaticLink(target=link_data))
        else:
            for link_dict in link_data:
                if "if" in link_dict:
                    links.append(FlowStepConditionLink(condition=link_dict['if'], target=link_dict['then']))
                else:
                    links.append(FlowStepFallbackLink(target=link_dict['else']))

        return links


@dataclass(slots=True)
class StartFlowStep(FlowStep):

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]):
        return cls(
            **FlowStep._load_base_fields(step_data)
        )


@dataclass(slots=True)
class EndFlowStep(FlowStep):

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]):
        return cls(
            **FlowStep._load_base_fields(step_data)
        )


@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    action: str  # 行动的名字 三种(action_xxx(做) action_response(说)  action_listen(停))
    args: dict[str, Any] = field(default_factory=dict)  # 行动所需的参数[action_response需要]

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]):
        return cls(
            **FlowStep._load_base_fields(step_data),
            action=step_data['action'],
            args=step_data.get('args', {})
        )


@dataclass(slots=True)
class CollectFlowStep(FlowStep):
    """
    注意：出现在业务流程侧
    """

    slot_name: str  # 槽位的名字
    response: ResponseDefinition  # 响应对象（响应内容更丰富）
    validate: SlotValidate | None = None  # 可选的

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]):
        return cls(
            **FlowStep._load_base_fields(step_data),
            slot_name=step_data['slot_name'],
            response=ResponseDefinition(
                text=step_data['response']['text'],
                mode=step_data['response'].get('mode', "static"),
                prompt=step_data['response'].get('prompt')
            ),
            validate=SlotValidate(
                condition=step_data['validate']['condition'],
                failure_response=ResponseDefinition(
                    text=step_data['validate']['failure_response']['text'],
                    mode=step_data['validate']['failure_response'].get('mode', "static"),
                    prompt=step_data['validate']['failure_response'].get('prompt')
                ) if step_data['validate'].get('failure_response') is not None else None
            ) if step_data.get('validate') is not None else None
        )


FLOW_STEP_TO_CLASS: dict[str, type[FlowStep]] = {
    "start": StartFlowStep,
    "collect": CollectFlowStep,
    "action": ActionFlowStep,
    "end": EndFlowStep

}

import yaml

if __name__ == '__main__':
    yaml_path = "user_flows.yml"
    with  open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_dict = yaml.safe_load(f.read())

    print(yaml_dict)
