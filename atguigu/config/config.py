from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 读取.env文件
PROJECT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = PROJECT_DIR / ".env"


class Settings(BaseSettings):
    """
    接收.env文件中的环境变量

    LLM_MODEL=qwen-plus
    LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
    LLM_API_KEY=sk-983bea5e73584a92950148b7df36a4b0

    COMMERCE_API_BASE_URL=http://192.168.200.133:18081

    DATABASE_URL=mysql+aiomysql://root:hzk686868@192.168.200.133:3306/customer_service?charset=utf8mb4

    APP_HOST=0.0.0.0
    APP_PORT=18082
    """

    llm_model: str  # 模型名字
    llm_base_url: str  # 模型服务平台的地址
    llm_api_key: str  # 模型服务平台的api_key
    commerce_api_base_url: str  # 中台服务的地址
    database_url: str  # AI应用对应的数据库地址
    app_host: str  # AI应用的访问域名
    app_port: int  # AI 应用的端口

    # 实例化SettingsConfigDict对象一定要有变量接收  并且变量的名字一定要叫model_config
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8",
                                      extra="ignore")  # extra="ignore" 忽略掉.env文件中多余的key_value


settings = Settings()  # type: ignore

if __name__ == '__main__':
    print(settings.llm_base_url)
