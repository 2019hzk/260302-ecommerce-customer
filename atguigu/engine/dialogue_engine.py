import time

from atguigu.domain.messages import ProcessResult, BotMessage, UserMessage, MessageType, FocusedObject
from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_plan import ClarifyReason
from atguigu.plan.validator import TurnPlanValidator
from atguigu.clarify.responder import ClarifyResponder
from atguigu.task.command.commands import SetSlotsCommand
from atguigu.task.flows.flows import FlowsList, Flow
from atguigu.task.flows.steps import CollectFlowStep
from atguigu.task.handler import TaskHandler
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.chitchat.handler import ChitChatHandler


class DialogueEngine:

    def __init__(self,
                 turn_planner: TurnPlanner,
                 turn_plan_validator: TurnPlanValidator,
                 clarify_responder: ClarifyResponder,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowledgeHandler,
                 chitchat_handler: ChitChatHandler
                 ):
        self._planner = turn_planner
        self._validator = turn_plan_validator
        self._responder = clarify_responder
        self._task_handler = task_handler
        self._knowledge_handler = knowledge_handler
        self._chitchat_handler = chitchat_handler

    async def process_message(self,
                              user_message: UserMessage,
                              state: DialogueState) -> ProcessResult:
        """
        :param dialogue_state:
        :return:
        """

        # 1. 准备session对象
        self._prepare_session(state)

        # 2. 开启turn
        self._start_turn(user_message, state)

        # 3. 处理消息类型(消息分流)
        # 3.1 文本消息类型
        if user_message.type is MessageType.TEXT:
            bot_messages: list[BotMessage] = await self._process_text_message(state,
                                                                              flows_list=self._task_handler.flows_list,
                                                                              knowledge_intents=self._knowledge_handler.intents
                                                                              )

        # 3.2 对象消息类型
        else:
            state.set_focused_object(user_message.object)
            bot_messages = await self._process_object_message(user_message.object, state, self._task_handler.flows_list)

        # 4. 轮次的提交
        state.pending_turn.bot_messages = bot_messages
        state.commit_pending_turn()

        # 5. 返回处理结果
        return ProcessResult(
            message_id=user_message.message_id,  # 前端未使用
            messages=bot_messages
        )

    def _prepare_session(self, state: DialogueState):
        """
        一定确保存在session对象
        Args:
            state:

        Returns:

        """

        # 1. 获取当前session对象
        current_session = state.current_session()

        # 2. 判断当前session是否存在
        # 2.2 当前session不存在
        if current_session is None:
            state.start_session()
        # 2.3  当前session存在
        else:
            now = time.time()
            # 2.3.1) 当前session过期了(关闭session不会把该session从sessions中移除掉。)
            if now - current_session.last_activated_at > 60 * 60:
                # a) 关闭当前session
                state.close_current_session()
                # b) 重置运行时对话状态
                state.reset_runtime_state_for_new_session()
                # c) 开启新的session
                state.start_session()
            # 2.3.2) 当前session没有过期，直接使用
            else:
                current_session.last_activated_at = now

        return

    def _start_turn(self,
                    user_message: UserMessage,
                    state: DialogueState):
        state.begin_turn(user_message)

    async def _process_text_message(self,
                                    state: DialogueState,
                                    *,
                                    flows_list: FlowsList,
                                    knowledge_intents: dict[str, KnowledgeIntent]) -> list[BotMessage]:

        # 1. 利用轮次规划器进行路由判断
        turn_plan = await self._planner.predict(state, flows_list, knowledge_intents)

        # 2. 利用轮次校验器校验轮次的结果
        validated = self._validator.validate(turn_plan, state, flows_list, knowledge_intents)

        # 3. 如果校验不通过，需要意图澄清器，澄清
        if not validated.valid:
            return await self._responder.respond(validated.reason, state)

        # 4. 如果校验通过，找到对应的三条轨道的处理器处理
        if turn_plan.task is not None:
            return await self._task_handler.handle(state, commands=turn_plan.task.commands)
        elif turn_plan.knowledge is not None:
            # pass
            return await self._knowledge_handler.handle(state,turn_plan.knowledge.intents)
        else:
            return await self._chitchat_handler.handle(turn_plan.chitchat.chat, state)

    async def _process_object_message(self,
                                      object_message: FocusedObject,
                                      state: DialogueState,
                                      flows_list: FlowsList
                                      ) -> list[BotMessage]:

        # 1. 尝试构建SetSlotsCommand
        command = self._try_resolve_set_slots_command(object_message, state, flows_list)

        # 2. 当前有业务流程有且业务流程某一步正好需要点击的卡片
        if command:
            return await self._task_handler.handle(state=state, commands=[command])  # 继续把流程往前推

        # 3.  当前有业务流程，但是当前业务流程某一步不缺点击的卡片
        if state.activated_task is not None:
            return await self._task_handler.handle(state=state, commands=[])  # 让流程执行 不会像前推，而是会继续这一步流程

        # 4. 当前业务流程没有
        return await self._responder.respond(reason=ClarifyReason.OBJECT_REQUIRES_INTENT, state=state)

    def _try_resolve_set_slots_command(self,
                                       object: FocusedObject,
                                       state: DialogueState,
                                       flows_list: FlowsList
                                       ) -> SetSlotsCommand | None:

        if object.type == "order":
            if self._is_build_set_slots_command("order_number", state, flows_list):
                return SetSlotsCommand(command="set_slots", slots={"order_number": object.id})  # 订单号
            return None

        if object.type == "product":
            if self._is_build_set_slots_command("product_id", state, flows_list):
                return SetSlotsCommand(command="set_slots", slots={"product_id": object.id})  # 商品编号

            return None

        return None

    def _is_build_set_slots_command(self,
                                    slot_name: str,
                                    state: DialogueState,
                                    flows_list: FlowsList) -> bool:
        """
        处理点击卡片的三种情况
        1. 有业务流程，且正好缺---->True
        2. 有业务流程，不缺---->False
        3. 没有业务流程 （缺与不缺不重要）---False
        Args:
            slot_name:
            state:
            flows_list:

        Returns: True: 能构建SetSlotsCommand False：不能构建SetSlotsCommand

        """

        # 1. 获取当前业务流程(上下文)
        activated_task = state.activated_task

        # 2. 判断当前业务流程是否存在
        if activated_task is None:
            return False

        # 3. 当前业务流程是存在（防御性代码）
        flow_id = activated_task.flow_id
        flow = flows_list.get_flow_by_flow_id(flow_id)
        if flow is None:
            return False

        # 4. 获取step_id
        step_id = activated_task.step_id
        step = flow.get_step_by_step_id(step_id)
        if not isinstance(step, CollectFlowStep):
            return False

        return step.slot_name == slot_name  # 区分当前业务流程这一步是否需要点击对象  返回True 刚好需要  返回False  不需要
