from dataclasses import dataclass, field

from atguigu.task.flows.steps import FlowStep


@dataclass(slots=True)
class FlowSlot:
    """
    业务流程的槽位
    """
    slot_name: str  # 字典中的KEY
    type: str
    label: str
    description: str


@dataclass(slots=True)
class Flow:
    """
    流程
    """
    flow_id: str
    flow_name: str
    description: str
    steps: list[FlowStep]  # 步骤（节点）具体化
    slots: dict[str,FlowSlot] =field(default_factory=dict)   # 将某一个业务流程中需要收集的槽位信息额外的补充到Flow对象的slots属性中（LLM用到）




@dataclass(slots=True)
class FlowsList:
    """
    全部流程配置（slots/flows）
    未来不是说只承载某一个yaml文件（两个YAML文件都要承载）
    """

    flows: list[Flow]
    slots: dict[str, FlowSlot] = field(default_factory=dict)
