from atguigu.domain.contexts import CanceledSystemContext, TaskContext, InterruptedSystemContext, StartedSystemContext
from atguigu.domain.state import DialogueState
from atguigu.task.command.commands import Command, StartFlowCommand, SetSlotsCommand, ResumeFlowCommand, \
    CancelFlowCommand
from atguigu.task.flows.flows import FlowsList


class CommandProcessor:
    def process_commands(self,
                         commands: list[Command],
                         state: DialogueState,
                         flows_list: FlowsList):
        """
        职责：根据commands中的命令，分别处理命令对应的动作(本质:[是修改state中和任务相关的属性]，供下一个组件流程推进器使用)
        Args:
            commands:
            state:
            flows_list:

        Returns:

        """
        for command in commands:
            self._apply(command, state, flows_list)

    def _apply(self,
               command: Command,
               state: DialogueState,
               flows_list: FlowsList):
        """
        职责： 根据每个具体的命令类型，执行对应的逻辑处理
        Args:
            command:
            state:
            flows_list:

        Returns:

        """

        if isinstance(command, StartFlowCommand):
            self._start_flow(command, state, flows_list)
        elif isinstance(command, SetSlotsCommand):  # 最简单
            self.update_slots(command, state)
        elif isinstance(command, ResumeFlowCommand):
            self._resume_flow(command, state, flows_list)
        elif isinstance(command, CancelFlowCommand):  # 比较简单
            self._cancel_flow(state, flows_list)
        else:
            pass

    def _start_flow(self,
                    command: StartFlowCommand,
                    state: DialogueState,
                    flows_list: FlowsList):
        """

        职责：修改state中和任务相关的属性
        Args:
            command:
            state:
            flows_list:

        Returns:

        """

        # 1. 获取目标业务流程ID
        start_flow_id = command.flow

        # 2. 获取目标业务流程的名字
        start_flow_name = flows_list.get_flow_by_flow_id(start_flow_id).flow_name

        # 3. 获取当前业务流程上下文对象
        activated_task = state.activated_task

        # 4. 判断当前活跃业务流程上下文对象
        # 4.1 当前存在业务流程
        if activated_task is not None:
            # a) 当前正在执行的业务流程和目标流程一样
            if activated_task.flow_id == start_flow_id:
                return  # 不用改state 什么都不做

            # b) 删除暂停栈中和目标流程相同的业务流程上下文对象
            state.remove_paused_tasks(flow_id=start_flow_id)

            # c) 获取中断业务流程的流程ID & 名字
            interrupted_flow_id = activated_task.flow_id
            interrupted_flow_name = flows_list.get_flow_by_flow_id(interrupted_flow_id).flow_name

            # d) 中断当前正在执行的业务流程上下文
            state.interrupt_activated_task()

            # e) "激活业务流程"上下文
            state.start_task(TaskContext(
                flow_id=start_flow_id,
                step_id="start"
            ))
            # f) 激活"中断系统流程"上下文
            state.start_system_task(InterruptedSystemContext(
                flow_id="system_task_interrupted",
                step_id="start",
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,
                started_flow_id=start_flow_id,
                started_flow_name=start_flow_name
            ))

        # 4.2 当前不存在业务流程
        else:

            # a) 删除暂停栈中和目标流程相同的业务流程上下文对象
            state.remove_paused_tasks(flow_id=start_flow_id)

            # b) “激活业务流程”上下文
            state.start_task(TaskContext(
                flow_id=start_flow_id,
                step_id="start"
            ))

            # c) ”激活开启系统流程“上下文
            state.start_system_task(StartedSystemContext(
                flow_id="system_task_started",
                step_id="start",
                started_flow_id=start_flow_id,
                started_flow_name=start_flow_name
            ))


    def update_slots(self,
                     command: SetSlotsCommand,
                     state: DialogueState):
        """
        职责：修改state中activated_task的slots属性【将传入过来的槽位信息【槽位名:槽位值】放到业务流程的slots中】
        来源1：文本消息-----LLM生成---转成了SetSlotsCommand
        来源2：对象消息【不会经过LLM处理】-----自己手动构建的SetSlotsCommands
        Args:
            command:
            state:

        Returns:

        """
        state.set_slots(command.slots)  # 最简单

    def _resume_flow(self,
                     command: ResumeFlowCommand,
                     state: DialogueState,
                     flows_list: FlowsList):
        pass

    def _cancel_flow(self,
                     state: DialogueState,
                     flows_list: FlowsList):
        """
        职责：
        1.修改state中的activated_task和activated_system_task【None】
        2.激活 system_task_canceled：精准，为了让用户看到 “好的，xxx 业务流程，先帮你取消”开场白

        Args:
            state:
            flows_list:

        Returns:

        """

        # 1. 获取当前业务流程上下文对象
        activate_task = state.activated_task

        # 2. 清空当前业务流程&系统流程
        state.cancel_activated_task()

        # 3. 激活取消系统流程上下文
        state.start_system_task(CanceledSystemContext(
            flow_id="system_task_canceled",
            step_id="start",
            canceled_flow_id=activate_task.flow_id,  # 取消的业务流程ID
            canceled_flow_name=flows_list.get_flow_by_flow_id(activate_task.flow_id).flow_name  # 取消的业务流程名字
        ))
