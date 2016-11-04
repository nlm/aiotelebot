import asyncio
from .abc import UpdateHandler

class AsyncUpdateHandler(UpdateHandler):

    def handle_update(self, update):
        pass

DefaultUpdateHandler = AsyncUpdateHandler
