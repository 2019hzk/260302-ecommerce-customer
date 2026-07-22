import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from atguigu.domain.messages import UserMessage, FocusedObject, BotMessage
from atguigu.domain.contexts import SystemContext, TaskContext


@dataclass(slots=True)
class Turn:
    """
    轮次：用户消息  机器人回复的消息[多条] 最小单元
    """
    turn_id: str  # 轮次id
    user_message: UserMessage
    bot_messages: list[BotMessage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_message": UserMessage.to_dict(self.user_message),
            "bot_messages": [BotMessage.to_dict(bot_msg) for bot_msg in self.bot_messages]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Turn":
        return cls(
            turn_id=data['turn_id'],
            user_message=UserMessage.from_dict(data['user_message']),
            bot_messages=[BotMessage.from_dict(bot_msg_dict) for bot_msg_dict in data['bot_messages']]
        )


@dataclass(slots=True)
class Session:
    """
    一次会话会包含多轮 session--->turn(1:n)
    会话：session创建时间 session活跃的时间(last_activated_at)
    """
    session_id: str
    started_at: float
    last_activated_at: float
    closed_at: float | None = None  # 有值：该session关闭过 没值：该session未关闭（未做主动关闭session 通过超时【60min】关闭session）
    turns: list[Turn] = field(default_factory=list)  # 最核心

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_activated_at": self.last_activated_at,
            "closed_at": self.closed_at,
            "turns": [Turn.to_dict(turn) for turn in self.turns]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        return cls(
            session_id=data['session_id'],
            started_at=data['started_at'],
            last_activated_at=data['last_activated_at'],
            closed_at=data['closed_at'],
            turns=[Turn.from_dict(turn_dict) for turn_dict in data['turns']]
        )


@dataclass(slots=True)
class DialogueState:
    """
    用户完整对话状态聚合根
    1. 任务相关----TasKContext   SystemContext
    2. 卡片相关----FocusedObject
    3. 会话session相关的【Turn轮次】 Session  Turn

    4. 缓存区
    """
    sender_id: str  # 用户ID
    activated_task: TaskContext | None = None  # 当前活跃的"业务流程"任务的（TaskContext）
    paused_tasks: list[TaskContext] = field(default_factory=list)  # 挂起"业务流程"任务 注意：paused_tasks 不会存储系统流程任务
    activated_system_task: SystemContext | None = None  # 当前"系统流程"任务（SystemContext）
    focused_object: FocusedObject | None = None
    sessions: list[Session] = field(default_factory=list)
    current_session_id: str | None = None
    pending_turn: Turn | None = None  # 缓冲区：后续引擎操作的轮次对象不在是Turn 而是pending_turn 可以保证轮次信息入库的完整性

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "activated_task": TaskContext.to_dict(self.activated_task) if self.activated_task is not None else None,
            "paused_tasks": [TaskContext.to_dict(paused_task) for paused_task in self.paused_tasks],
            "activated_system_task": SystemContext.to_dict(
                self.activated_system_task) if self.activated_system_task is not None else None,
            "focused_object": FocusedObject.to_dict(self.focused_object) if self.focused_object is not None else None,
            "sessions": [Session.to_dict(session) for session in self.sessions],
            "current_session_id": self.current_session_id,
            "pending_turn": Turn.to_dict(self.pending_turn) if self.pending_turn is not None else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DialogueState":
        return cls(
            sender_id=data['sender_id'],
            activated_task=TaskContext.from_dict(data['activated_task']) if data[
                                                                                'activated_task'] is not None else None,
            paused_tasks=[TaskContext.from_dict(paused_task_dict) for paused_task_dict in data['paused_tasks']],
            activated_system_task=SystemContext.from_dict(data['activated_system_task']) if data[
                                                                                                'activated_system_task'] is not None else None,
            focused_object=FocusedObject.from_dict(data['focused_object']) if data[
                                                                                  'focused_object'] is not None else None,
            sessions=[Session.from_dict(session_dict) for session_dict in data['sessions']],
            current_session_id=data['current_session_id'],
            pending_turn=Turn.from_dict(data['pending_turn']) if data['pending_turn'] is not None else None
        )

    # ===================================（业务、系统）流程任务相关==================================

    def start_task(self, task_context: TaskContext):
        """
        职责：开启一个新的"业务流程"任务
        :return:
        """
        self.activated_task = task_context

    def end_activated_task(self):
        """
        职责：结束当前执行的"业务流程"任务
        :return:
        """
        self.activated_task = None

    def cancel_activated_task(self):
        """
        职责：取消当前正在执行的"业务流程任务"以及"系统流程任务"
        :return:
        """

        self.activated_task = None
        self.activated_system_task = None

    def interrupt_activated_task(self):
        """
        职责：中断(挂起)正在执行的"业务流程任务"
        :return:
        """

        # 1. 把当前正在执行的业务流程上下文获取到加入进paused_tasks
        self.paused_tasks.append(self.activated_task)

        # 2. 清空当前正在执行业务流程任务的上下文
        self.activated_task = None

    def resume_task(self, flow_id: str | None = None) -> bool:
        """
        职责：恢复中断的业务流程任务
        模式一：没有指定恢业务流程任务的流程ID 从栈顶恢复【内置】
        模式：从栈中根据指定的业务流程任务的流程ID 恢复【精确恢复】
        :return:  bool 恢复出来 成功 未恢复出来 失败
        """

        # 1. 业务流程任务的暂停栈中是否有元素
        if not self.paused_tasks:
            return False

        # 2.内置恢复
        if flow_id is None:
            paused_task = self.paused_tasks.pop()  # pop
            self.activated_task = paused_task
            return True

        # 3. 精确恢复
        for index, paused_task in enumerate(self.paused_tasks):
            if paused_task.flow_id == flow_id:
                self.activated_task = paused_task
                del self.paused_tasks[index]
                return True
        return False

    def start_system_task(self, system_context: SystemContext):
        """
        职责：开启一个新的"系统流程任务"
        :param system_context:
        :return:
        """
        self.activated_system_task = system_context

    def end_system_task(self):
        """
        职责：结束正在执行的"系统流程任务"
        :return:
        """

        self.activated_system_task = None

    def current_task(self):
        """
        职责：返回当前应用中系统流程任务上下文或者业务流程任务上下文
        如果当前应用中既有 系统流程任务上下文又有业务流程上下文，优选返回系统流程任务上下文。过场表要先说
        调用者：FlowExecutor 通过while true 循环调用current_task 方法
        :return:
        """
        return self.activated_system_task or self.activated_task

    # ===================================（槽位）相关==================================

    def set_slots(self, slots: dict[str, Any]):

        if self.activated_task is not None:
            self.activated_task.slots.update(slots)

    def remove_slot(self, slot_name: str):
        if self.activated_task is not None:
            self.activated_task.slots.pop(slot_name)


    # ===================================（会话session）相关==================================
    def start_session(self):
        now = time.time()
        # 实例化session
        session = Session(session_id=str(uuid.uuid4()),
                          started_at=now,
                          last_activated_at=now)

        self.sessions.append(session)
        self.current_session_id = session.session_id

    def current_session(self) -> Session | None:
        for session in self.sessions:
            if session.session_id == self.current_session_id:
                return session
        return None

    def close_current_session(self):
        self.current_session().closed_at = time.time()
        self.current_session_id = None

    def reset_runtime_state_for_new_session(self):
        self.activated_task = None
        self.activated_system_task = None
        self.paused_tasks = []
        self.focused_object = None
        self.pending_turn=None

    # ===================================（pending_turn）相关==================================
    def begin_turn(self, message: UserMessage):
        self.pending_turn = Turn(
            turn_id=str(uuid.uuid4()),
            user_message=message,
            bot_messages=[]     # 引擎后续处理完之后 将得到的bot_message追加到bot_messages中
        )

    def commit_pending_turn(self):
        self.current_session().turns.append(self.pending_turn)
        self.pending_turn = None    # 及时清空缓冲区 为了接收下一个轮次(turn)

    # ===================================（卡片）相关==================================
    def set_focused_object(self, object: FocusedObject):
        self.focused_object = object









