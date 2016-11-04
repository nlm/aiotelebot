from abc import ABCMeta, abstractmethod

class UpdateDispatcher(metaclass=ABCMeta):
    pass

class UpdateHandler(metaclass=ABCMeta):
    @abstractmethod
    def handle_update(self, update):
        pass
