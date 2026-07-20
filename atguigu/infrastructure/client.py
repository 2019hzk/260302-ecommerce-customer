import asyncio
from httpx import AsyncClient

http_client: AsyncClient | None = None


def init_http_client():
    """定义http异步客户端"""
    global http_client

    http_client = AsyncClient(timeout=120, trust_env=False)  # 禁用掉代理访问


async def dispose_http_client():
    """
    关闭http异步客户端
    :return:
    """
    await http_client.aclose()


async def main_test():
    init_http_client()
    response = await  http_client.get(url="http://192.168.200.133:18081/orders/A20260408002")

    print(response.json())


if __name__ == '__main__':
    asyncio.run(main_test())
