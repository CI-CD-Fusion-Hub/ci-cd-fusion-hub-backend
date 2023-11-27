from abc import ABC, abstractmethod
from typing import List


class BaseClient(ABC):
    @abstractmethod
    async def check_connection(self):
        pass

    @abstractmethod
    async def get_pipelines_list(self):
        pass

    @abstractmethod
    async def get_pipelines_list_by_pattern(self, regex_pattern: str) -> List:
        pass
