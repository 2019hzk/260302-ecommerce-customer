from dataclasses import asdict

from atguigu.domain.contexts import CollectedInformationSystemContext
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.runner import ActionRunner, ActionCall
from atguigu.task.flows.flows import FlowsList
from atguigu.task.flows.links import FlowStepStaticLink, FlowStepConditionLink, FlowStepFallbackLink
from atguigu.task.flows.steps import FlowStep, StartFlowStep, EndFlowStep, ActionFlowStep, CollectFlowStep


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
            action_call: ActionCall = self._advance_flow_util_action(flows_list, state)

            # 2. 判断action_call有值 判断action_name,如果action_name是action_xxx才调用action 如果action_name是action_response(不用管) 如果action_name是action_listen
            if action_call.action_name == "action_listen":
                break
            else:
                action_result = await action_runner.run(action_call, state)

                final_messages.extend(action_result.messages)
                state.set_slots(action_result.slots)

        return final_messages

    def _advance_flow_util_action(self,
                                  flows_list: FlowsList,
                                  state: DialogueState) -> ActionCall:
        """
        职责：对内真正推进流程
        Args:
            flows_list:
            state:

        Returns:

        """

        while True:

            # 1. 获取当前的上下文对象 系统流程上下文或者业务流程上下文【先获取到的是系统流程上下文】
            current_task = state.current_task()
            if current_task is None:  # 业务流程推进完毕
                return ActionCall(action_name="action_listen")

            # 2. 获取要推进的流程ID(业务流程ID 系统流程ID)
            flow_id = current_task.flow_id

            # 3. 获取流程对象(业务流程对象 系统流程对象)
            flow = flows_list.get_flow_by_flow_id(flow_id)

            # 4. 获取步骤ID
            step_id = current_task.step_id

            # 5. 获取步骤对象
            step = flow.get_step_by_step_id(step_id)

            # 6. 执行步骤
            action_call = self._run_step(step, state)

            if action_call is not None:
                return action_call

    def _run_step(self,
                  step: FlowStep,
                  state: DialogueState) -> ActionCall | None:
        """
        职责step
        Args:
            step:
            flows_list:
            state:

        Returns:

        """
        if isinstance(step, StartFlowStep):
            return self._run_start_step(step, state)
        elif isinstance(step, EndFlowStep):
            return self._run_end_step(state)
        elif isinstance(step, ActionFlowStep):
            return self._run_action_step(step, state)
        elif isinstance(step, CollectFlowStep):
            return self._run_collect_step(step, state)
        else:
            return None

    def _run_start_step(self,
                        step: StartFlowStep,
                        state: DialogueState) -> None:

        # 1. 推进下一步
        self._advance_flow_step(step, state)

        # 2. 返回None
        return None

    def _advance_flow_step(self,
                           step: FlowStep,
                           state: DialogueState):

        # 1. 根据当前step找到下一个step_id
        selected_id = self._select_step_id(step, state)

        # 2. 更新selected_id
        state.current_task().step_id = selected_id

    def _select_step_id(self,
                        step: FlowStep,
                        state: DialogueState):
        for next_link in step.next:

            if isinstance(next_link, FlowStepStaticLink):
                return next_link.target  # 下一条边的ID

            if isinstance(next_link, FlowStepConditionLink):
                validated = self._eval_condition(next_link.condition, state)
                if validated:
                    return next_link.target
            if isinstance(next_link, FlowStepFallbackLink):
                return next_link.target  # 下一条边的ID

    def _eval_condition(self,
                        condition: str,
                        state: DialogueState) -> bool:

        #  "slots.get('product_id')"    # eval

        context = {
            'slots': state.activated_task.slots,  # state.activated_task.slots:{"order_number":"123456"}
            'context': asdict(state.activated_system_task) if state.activated_system_task is not None else {}
        }

        return eval(condition, {}, context)

    def _run_end_step(self, state: DialogueState) -> None:
        """

        Args:
            state:

        Returns:

        """
        if state.activated_system_task is not None:
            state.end_system_task()  # 下一次才能切换到业务流程

        elif state.activated_task is not None:
            state.end_activated_task()
        else:
            pass

        return None

    def _run_action_step(self,
                         step: ActionFlowStep,
                         state) -> ActionCall:
        # 1. 推进下一步
        self._advance_flow_step(step, state)

        # 2. 构建Action
        action_kwargs = step.args
        if isinstance(step.args, str):
            action_kwargs = asdict(state.activated_system_task)['response']  # 字典 就可以将业务侧定义的槽位描述 带出去

        # 3. 返回Action
        return ActionCall(action_name=step.action, action_kwargs=action_kwargs)

    def _run_collect_step(self,
                          step: CollectFlowStep,
                          state: DialogueState) -> ActionCall | None:
        """
        收集槽位信息（业务流程会进来）
        特点：
        1、 用户可能会配置槽位的校验
        2、 该方法会执行两次
        2.1 第一次执行的目的是为了触发system_collect_information系统流程，收集用户槽位信息
        2.2 第二次执行的目的是对用户填写的槽位信息做校验
        a) 如果校验通过，执行后面的步骤
        b) 如果校验不通过，删除填错的槽位，重新触发system_collect_information系统流程，在收集用户的槽位信息
        Args:
            step:
            state:

        Returns:

        """
        # 1. 尝试利用点击的卡片
        self._try_fill_slots_from_focused_object(step, state)

        # 2. 判断
        if state.activated_task.slots.get(step.slot_name):
            # 第二次进来，代表用户填写了槽位，判断填写的槽位是否合法
            # 配置了校验开关
            if step.validate:
                if self._eval_condition(step.validate.condition, state):
                    # 推进下一步
                    self._advance_flow_step(step, state)
                    # 返回None
                    return None
                else:
                    # 移除填错的槽位
                    state.remove_slot(step.slot_name)
                    # 给响应
                    if step.validate.failure_response is None:
                        # 给默认的响应
                        return ActionCall(action_name="action_response",
                                          action_kwargs={"text": "您填写的错误信息有误，请你重新填写"})
                    else:
                        # 给自己配置的错误响应
                        return ActionCall(action_name="action_response",
                                          action_kwargs=asdict(step.validate.failure_response))

            # 没有在YAML为collect类型的步骤配置校验
            else:
                # 推进下一步
                self._advance_flow_step(step, state)
                # 返回None
                return None
        else:
            # 激活收集槽位信息的系统流程
            state.start_system_task(CollectedInformationSystemContext(
                flow_id="system_collect_information",
                step_id="start",
                response=asdict(step.response),
                slot_name=step.slot_name
            ))

            return None  # 只需要返回None 并且不可推下一步

    def _try_fill_slots_from_focused_object(self,
                                            step: CollectFlowStep,
                                            state: DialogueState):

        # 1. 判断当前业务流程以及卡片对象是否有
        if state.activated_task is None or state.focused_object is None:
            return

        # 2. 利用点击的卡片
        excepted_slots_mapping = {
            "order": "order_number",
            "product": "product_id"
        }
        excepted_slots = excepted_slots_mapping.get(state.focused_object.type)

        # 3. 当前业务流程的这一步需要的槽位名是否和期望的槽位一致
        if step.slot_name == excepted_slots and not state.activated_task.slots.get(step.slot_name):
            state.set_slots({step.slot_name: state.focused_object.id})


if __name__ == '__main__':
    # condition_str= "slots.get('product_id')=='12345'"
    condition_str = "slots.get('product_id')=='123456' and data.get('name')=='zs'"

    context = {
        "slots": {
            "product_id": "123456"
        },
        "data": {
            "name": "ls"
        }
    }

    print(eval(condition_str, {}, context))
