from abc import ABC, abstractmethod


class BaseClient(ABC):
    @abstractmethod
    def check_connection(self):
        pass
