from sqlalchemy.orm import  Mapped,mapped_column
from sqlalchemy import  TEXT

from atguigu.repository.base import  Base

class DialogueRecord(Base):
    __tablename__ = "dialogue_states"

    sender_id: Mapped[str]= mapped_column(primary_key=True)   # sender_id列是主键   Mapped[str]---推断sender_id列的类型是varchar  给ide提供代码补全能力和类型提示
    state_json: Mapped[str]= mapped_column(TEXT,nullable=False,default="{}")

