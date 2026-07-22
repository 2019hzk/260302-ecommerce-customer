from fastapi import FastAPI
from atguigu.api import chat_router
from atguigu.infrastructure.database import init_db_engine, dispose_db_engine


async def lifespan(_: FastAPI):
    """
    生命周期的lifespan函数一定要接收fastapi实例，哪怕函数内不用也要写。
    Args:
        fastapi:

    Returns:

    """
    # 应用启动
    print("应用启动期间回调到...")
    init_db_engine()
    yield  # 【分割信号/分界线】，为了区分应用启动的时候执行初始化资源 应用关闭执行资源的释放
    print("应用关闭回调到...")
    await dispose_db_engine()


app = FastAPI(lifespan=lifespan)

app.include_router(chat_router.router)
