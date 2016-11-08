import asyncio
from abc import (ABCMeta, abstractmethod,
                 abstractclassmethod, abstractstaticmethod)

class AsyncBotCore(metaclass=ABCMeta):

    @abstractmethod
    @asyncio.coroutine
    def input
