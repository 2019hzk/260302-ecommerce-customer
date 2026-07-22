import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState
from atguigu.repository.dialogue_record import DialogueRecord


class DialogueRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def load_state(self, sender_id: str) -> DialogueState:
        """
        根据用户ID 从数据库中查询该用户的完整对话状态
        Args:
            sender_id:  用户ID

        Returns:
            DialogueState: 用户的完整对话状态

        """

        # 1. 构建SQL语句 execute(text("select * from dialogue_sates where sender_id= 1234"))  CORE[连表的CURD] /ORM(单表的crud)
        stmt = select(DialogueRecord).where(DialogueRecord.sender_id == sender_id)

        # 2. 执行SQL语句
        cursor = await self._session.execute(stmt)

        # 3. 获取结果(解析结果)
        record = cursor.scalar_one_or_none()
        if record is None:
            return DialogueState(sender_id=sender_id)

        # 4. 处理
        state_dict = json.loads(record.state_json)

        # 5. 返回处理后的结果
        return DialogueState.from_dict(state_dict)

    async def save_state(self, dialogue_state:DialogueState):
        pass
