from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.flows.flows import FlowsList


class  FlowExecutor:
    async def executor_flow(self,
                            flows_list:FlowsList,
                            state:DialogueState)->list[BotMessage]:

        # TODO (推进流程)
        return [BotMessage(text="机器人回复")]

