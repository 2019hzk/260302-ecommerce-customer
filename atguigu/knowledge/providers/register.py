from atguigu.knowledge.providers.base import Provider


class ProviderRegister:


    def __init__(self, providers: list[Provider]):
        """
        定义一个字典结构--注册中心
        {"provider_id":Provider对象}
        Args:
            providers:

        Returns:

        """

        self._providers = {provider.provider_id: provider for provider in providers}

    def get_provider(self, provider_id: str) -> Provider:
        return self._providers[provider_id]
