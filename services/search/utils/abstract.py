from abc import ABC, abstractmethod


class AsyncSearchService(ABC):
    @abstractmethod
    async def get(
        self,
        index: str,
        id: str,
        **kwargs
    ):
        pass

    @abstractmethod
    async def search(self, index: str, body: dict, **kwargs):
        pass
