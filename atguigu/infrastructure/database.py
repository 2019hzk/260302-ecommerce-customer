"""
定义数据库的引擎以及连接工厂
"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from atguigu.config.config import settings

db_engine: AsyncEngine | None = None

session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db_engine():
    global db_engine, session_factory

    db_engine = create_async_engine(url=settings.database_url, echo=True)  # echo=True: 控制台显示SQL语句的执行
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)  # expire_on_commit=True/False


async def dispose_db_engine():
    await db_engine.dispose()


async def main_test():
    init_db_engine()

    async with session_factory() as session:
        result = await session.execute(text("select 1"))
        raw = result.mappings().fetchone()  # fetchone  # (1,)   mappings:{'1': 1}
        print(raw)

    await dispose_db_engine()


if __name__ == '__main__':
    asyncio.run(main_test())
