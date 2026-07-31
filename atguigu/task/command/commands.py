"""
各种command
总结：四种Command
开启业务流程对应Command
填写槽位信息对应Command
取消业务流程对应Command
恢复业务流程对应Command
"""

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Command:
    """
    四种命令的基类
    """
    command: str

    @staticmethod
    def from_dict(command_data: dict[str, Any]) -> "Command":
        command = command_data['command']

        clz = COMMAND_TO_CLASS[command]

        return clz(**command_data)


@dataclass(slots=True)
class StartFlowCommand(Command):
    flow: str  # 业务流程ID,不是业务流程对象


@dataclass(slots=True)
class SetSlotsCommand(Command):
    slots: dict[str, Any]


@dataclass(slots=True)
class CancelFlowCommand(Command):
    flow:str  | None=None   # 解包不会发生错误


@dataclass(slots=True)
class ResumeFlowCommand(Command):
    flow: str | None = None


COMMAND_TO_CLASS: dict[str, type[Command]] = {
    "start_flow": StartFlowCommand,
    "resume_flow": ResumeFlowCommand,
    "cancel_flow": CancelFlowCommand,
    "set_slots": SetSlotsCommand

}

if __name__ == '__main__':
    data = {"command": "start_flow", "flow": "order_status"}
    data1 = {"command": "resume_flow"}
    data2={"command": "set_slots", "slots": {"order_number": "123456"}}

    print(Command.from_dict(data))
    print(Command.from_dict(data1))
    print(Command.from_dict(data2))