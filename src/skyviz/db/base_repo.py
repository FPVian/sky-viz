from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def engine(self):
        pass
