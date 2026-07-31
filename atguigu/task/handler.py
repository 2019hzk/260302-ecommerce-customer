from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.runner import ActionRunner
from atguigu.task.command.commands import Command
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.flows.executor import FlowExecutor
from atguigu.task.flows.flows import FlowsList


class TaskHandler:

    def __init__(self,
                 flows_list: FlowsList,
                 command_processor: CommandProcessor,
                 flow_executor: FlowExecutor,
                 action_runner: ActionRunner
                 ):
        self.flows_list = flows_list
        self._command_processor = command_processor
        self._flow_executor = flow_executor
        self._action_runner = action_runner

    async def handle(self,
                     state: DialogueState,
                     commands: list[Command]) -> list[BotMessage]:
        """
        Args:
            state:
            commands:

        Returns:

        """

        # 1. 利用命令[指令]处理器处理对应的命令[指令]
        self._command_processor.process_commands(commands, state, self.flows_list)

        # 2. 利用流程推进器推荐流程
        bot_messages = await self._flow_executor.executor_flow(self.flows_list, self._action_runner, state)

        # 3. 返回机器人回复的消息
        return bot_messages
