from atguigu.domain.messages import UserMessage, ProcessResult
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository


class DialogueService:

    def __init__(self,
                 engine: DialogueEngine,
                 repository: DialogueRepository
                 ):
        self._engine = engine
        self._repository = repository

    async def process_message(self, user_message: UserMessage) -> ProcessResult:
        """
        每一轮对话都会做数据库读写操作和引擎的计算
        Args:
            user_message:

        Returns:

        """

        # 1. 从数据库中读取最新的状态
        dialogue_state = await self._repository.load_state(user_message.sender_id)

        # 2. 调用引擎做各种逻辑处理(调用LLM 进行路由分析、推进流程...)
        process_result = await self._engine.process_message(dialogue_state)

        # 3. 将引擎层修改后的最新状态存储到数据库中
        await self._repository.save_state(user_message.sender_id,dialogue_state)

        # 4. 返回引擎层处理后的结果(机器人回复)
        return process_result
