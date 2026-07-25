import time

from atguigu.domain.messages import ProcessResult, BotMessage, UserMessage, MessageType
from atguigu.domain.state import DialogueState
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.validator import TurnPlanValidator
from atguigu.clarify.responder import ClarifyResponder
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
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chitchat_handler = chitchat_handler

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
            bot_messages: list[BotMessage] = await self._process_text_message(state)

        # 3.2 对象消息类型
        else:
            state.set_focused_object(user_message.object)
            bot_messages = await self._process_object_message(state)

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

    async def _process_text_message(self, state: DialogueState) -> list[BotMessage]:

        # 1. 利用轮次规划器进行路由判断
        turn_plan = await self._planner.predict(state)

        # 2. 利用轮次校验器校验轮次的结果(TODO)
        validated = self._validator.validate(turn_plan)

        # 3. 如果校验不通过，需要意图澄清器，澄清(TODO)
        if  not validated:
            return  self._responder.respond(validated,state),

        # 4. 如果校验通过，找到对应的三条轨道的处理器处理(TODO)
        # 5. 将三条轨道处理后的结果 返回

        pass

    async def _process_object_message(self,
                                      state: DialogueState) -> list[BotMessage]:
        # TODO (周一实现)
        pass
