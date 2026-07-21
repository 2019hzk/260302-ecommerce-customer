import asyncio

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import String
from atguigu.config.config import settings


class Base(DeclarativeBase):
    pass


# 假设这是你的商品表模型
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))


db_engine = create_async_engine(url=settings.database_url, echo=True)
# 在提交数据库事务之后，依然保留内存中已查询出来的对象数据
session_factory = async_sessionmaker(db_engine, expire_on_commit=False)  # 故意设为 True


async def demo():
    async with session_factory() as session:
        # 1. 异步查出一个商品对象
        product = await session.get(Product, 1)
        print(f"第一次次读取{product.title}")  # 正常
        # 2. 提交事务
        await session.commit()
        # 3. 再次尝试读取属性
        print(f"第二次读取{product.title}")  # 异常: 底层会在用异步连接查询数据库 获取数据库中最新的对象以及对象的值出来

        await db_engine.dispose()

if __name__ == '__main__':
    asyncio.run(demo())
