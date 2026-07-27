from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.command.commands import Command
from atguigu.task.flows.flows import FlowsList


class TaskHandler:

    def __init__(self, flows_list: FlowsList):
        self.flows_list = flows_list

    async  def handle(self,
               state:DialogueState,
               commands:list[Command])->list[BotMessage]:


        """
        TODO :根据commands中的命令  真正的处理流程(开启业务流程、恢复业务流程、取消业务流程、给业务流程设置槽位信息)
        Args:
            state:
            commands:

        Returns:

        """
        pass

