from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.runner import ActionRunner, ActionCall
from atguigu.task.flows.flows import FlowsList


class FlowExecutor:
    async def executor_flow(self,
                            flows_list: FlowsList,
                            action_runner: ActionRunner,
                            state: DialogueState) -> list[BotMessage]:

        """
         职责：根据processor修改后的state 推进流程(业务流程、系统流程)
        Args:
            flows_list:
            action_runner:
            state:

        Returns:

        """

        final_messages = []
        while True:
            ###### 对外执行行动Action

            # 1. 找到action步骤类型
            action_call: ActionCall = self._advance_flow_util_action(flows_list,state)

            # 2. 判断action_call有值 判断action_name,如果action_name是action_xxx才调用action 如果action_name是action_response(不用管) 如果action_name是action_listen
            if action_call.action_name == "action_listen":
                break
            else:
                action_result=await action_runner.run(action_call)

                final_messages.extend(action_result.messages)
                state.set_slots(action_result.slots)

        return final_messages

    def _advance_flow_util_action(self,
                                  flows_list:FlowsList,
                                  state:DialogueState)->ActionCall:
        """
        职责：对内真正推进流程
        Args:
            flows_list:
            state:

        Returns:

        """

        while True:

            # 1. 获取当前的上下文对象 系统流程上下文或者业务流程上下文【先获取到的是系统流程上下文】
            current_task=state.current_task()

            # 2. 获取要推进的流程ID(业务流程ID 系统流程ID)
            flow_id= current_task.flow_id

            # 3. 获取流程对象(业务流程对象 系统流程对象)
            flow= flows_list.get_flow_by_flow_id(flow_id)

            # 4. 获取步骤ID
            step_id=current_task.step_id

            # 5. 获取步骤对象
            step= flow.get_step_by_step_id(step_id)

            action_call=self._run_step()

            if action_call is not None:
                return action_call








