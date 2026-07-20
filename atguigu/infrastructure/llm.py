"""
定义LLM 客户端
标准写法（PEP8规范）
# 1. sdk自带的依赖包

# 2. 第三组件的依赖包

# 3. 自己应用的依赖包
"""
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from atguigu.config.config import settings

llm_client: BaseChatModel = init_chat_model(
    model=settings.llm_model,
    model_provider="openai",
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    temperature=0,  # 尽量保证同样的输入得到同样的输出（稳定性）
    timeout=60
)
