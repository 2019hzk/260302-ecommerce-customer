from typing import Any
from dataclasses import dataclass, field, asdict

"""

TaskContext  SystemContext 
1. 什么时候创建（实例化）创建新的业务流程、中断业务流程、取消业务流程、恢复业务流程 业务流程需要收集槽位信息的时候创建
2. 谁来调用（自研轻量级的组件FlowExecutor:流程推进器）
1、2 不用关心  
"""


@dataclass(slots=True)
class TaskContext:
    """
    职责：记住（存储）当前在执行哪个业务流程任务、业务流程任务走到哪一步（step）、业务流程走到的这一步(step)收集到哪些数据或者要不要收集数据
    """
    flow_id: str  # 当前正在执行的业务流程任务的流程ID(变化)
    step_id: str  # 当前正在执行的业务流程任务的流程对应步骤ID(变化)
    slots: dict[str, Any] = field(default_factory=dict)  # 业务流程需要的数据信息（名字【槽位名】、值【槽位值】）（变化）

    def to_dict(self) -> dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "step_id": self.step_id,
            "slots": dict(self.slots)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskContext":
        return cls(
            flow_id=data['flow_id'],
            step_id=data['step_id'],
            slots=dict(data['slots'])
        )


@dataclass(slots=True)
class SystemContext:
    """
     职责：
     记住（存储）当前这是什么过场【创建一个新的业务流程对应的过场、中断当前在执行的业务流程的过场、恢复中断的业务流程过场、取消业务流程的过程、收集槽位信息业务流程的过场】
     涉及哪几个业务流程【一个业务流程、两个业务流程（中断过场）】
     过场说到哪了（step_id）
    """
    flow_id: str  # 正在执行的系统流程任务的流程ID（过场ID）
    step_id: str  # 正在执行的系统流程任务流程对应的步骤ID

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemContext":
        flow_id = data['flow_id']
        clz = SYSTEM_CONTEXT_TO_CLASS[flow_id]
        return clz(**data)

@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    started_flow_id: str
    started_flow_name: str  # 正在执行的业务流程的流程名字


@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    resumed_flow_id: str
    resumed_flow_name: str


@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    interrupted_flow_id: str
    interrupted_flow_name: str
    started_flow_id: str
    started_flow_name: str


@dataclass(slots=True)
class CanceledSystemContext(SystemContext):
    canceled_flow_id: str
    canceled_flow_name: str


@dataclass(slots=True)
class CollectedInformationSystemContext(SystemContext):
    response: dict[str, Any]
    slot_name: str  # 后面slot_name做判断


SYSTEM_CONTEXT_TO_CLASS: dict[str, Any] = {
    "system_task_started": StartedSystemContext,
    "system_task_resumed": ResumedSystemContext,
    "system_collect_information": CollectedInformationSystemContext,
    "system_task_interrupted": InterruptedSystemContext,
    "system_task_canceled": CanceledSystemContext,

}




