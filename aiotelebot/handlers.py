import asyncio
from abc import ABCMeta, abstractmethod

class UpdateHandler(metaclass=ABCMeta):

    @abstractmethod
    def handle_update(self, update):
        pass


class DefaultAsyncUpdateHandler(UpdateHandler):
    pass
