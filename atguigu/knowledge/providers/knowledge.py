import asyncio
import json
from typing import Any
from atguigu.config.config import  settings
from atguigu.infrastructure import  client

from atguigu.domain.state import DialogueState
from atguigu.knowledge.providers.base import Provider, KnowledgeChunk


class ApiOrderProvider(Provider):
    provider_id = "api.order"

    async def retrival(self, state: DialogueState) -> list[KnowledgeChunk]:
        """
        检索数据：数据源：不是只有RAG，文件、网络、数据库都是..
        从中台服务的订单接口检索数据
        Args:
            state:

        Returns:

        """
        focused_object = state.focused_object
        order_number = focused_object.id

        order_payload, logistics_payload = await asyncio.gather(
            self._fetch_order(order_number),
            self._fetch_logistics(order_number),
        )

        return [
            KnowledgeChunk(
                content="订单与物流信息：\n"
                        + json.dumps(
                    {
                        "order_number": order_number,
                        "order": order_payload,
                        "logistics": logistics_payload,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        ]

    async def _fetch_order(self, order_number) -> dict[str, Any]:
        url = f"{settings.commerce_api_base_url}/orders/{order_number}"
        response = await client.http_client.get(url)
        return response.json()["data"]

    async def _fetch_logistics(self, order_number) -> dict[str, Any]:
        url = f"{settings.commerce_api_base_url}/orders/{order_number}/logistics"
        response = await client.http_client.get(url)
        return response.json().get("data", {})




class  ApiProductProvider(Provider):
    provider_id = "api.product"

    async def retrival(self, state: DialogueState) -> list[KnowledgeChunk]:
        """
           从中台服务的商品接口检索数据
        Args:
            state:

        Returns:

        """
        product_id = state.focused_object.id
        data: dict[str, Any] = await self._get_product_info_by_id(product_id)
        text = json.dumps(data, ensure_ascii=False, indent=2)
        return [KnowledgeChunk(content=f"商品信息:\n{text}")]

    async def _get_product_info_by_id(self, product_id: str) -> dict[str, Any]:
        url = f"{settings.commerce_api_base_url}/products/{product_id}"
        response = await client.http_client.get(url)
        return response.json()["data"]


class FAQDefaultProvider(Provider):

    provider_id = "faq.default"

    async def retrival(self, state: DialogueState) -> list[KnowledgeChunk]:
        """
        TODO 后面对接公司提供好的FAQ检索结果（开发好的、自己开发系统）
        Args:
            state:

        Returns:

        """
        return  [KnowledgeChunk(content="暂未对接FAQ,无法查询到有效的知识内容")]


class RAGDefaultProvider(Provider):
    provider_id = "rag.default"

    async def retrival(self, state: DialogueState) -> list[KnowledgeChunk]:
        """
        TODO 后面对接公司提供好的RAG检索结果(开发好的、自己开发系统)
        Args:
            state:

        Returns:

        """
        return [KnowledgeChunk(content="暂未对接RAG,无法查询到有效的知识内容")]




