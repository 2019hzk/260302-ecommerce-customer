import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert  # 注意

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

    async def save_state(self, sender_id: str, dialogue_state: DialogueState):
        """
        将引擎处理后的state 保存到数据库中
        不是直接保存，会涉及到修改。
        1. 如果第一次来(sender_id主键第一次没有生成，数据表中没有sender_id值) 保存
        2. 如果非第一次进来(sender_id主键已经生成，数据表中有sender_id这一列值) 修改
        注意:sender_id 是唯一的。

        Args:
            sender_id: 用户ID
            dialogue_state: 引擎修改后的状态

        Returns:

        """

        # 1. 处理数据
        dialogue_state_dict = DialogueState.to_dict(dialogue_state)

        # 2. 序列化
        dialogue_state_json = json.dumps(dialogue_state_dict)

        # 3. 构建SQL语句（自带插入和修改的判断。业务层不用再判断，SQL层自己判断） 注意：insert语句一定是sqlalchemy包下的方言包中具体数据库中的
        insert_stmt = insert(DialogueRecord).values(sender_id=sender_id, state_json=dialogue_state_json)
        #  on_duplicate_key_update:主键值或者唯一索引值
        update_stmt = insert_stmt.on_duplicate_key_update(state_json=insert_stmt.inserted.state_json)

        # 4. 执行SQL语句
        await self._session.execute(update_stmt)

        # 5. 手动提交
        await self._session.commit()
