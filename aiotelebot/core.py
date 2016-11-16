import asyncio
from .api.objects import Update

class TelegramBotCore(object):

    def __init__(self, bot, api_client):
        self._bot = bot
        self._client = api_client
        self._dispatcher = self.dispatcher()
        self._dispatcher.send(None)
        self._chats = {}
        self._log = logging.getLogger(__name__)

    @asyncio.coroutine
    def message_handler(self):
        return
        yield

    @asyncio.coroutine
    def dispatcher(self):
        result = None
        while True:
            update = yield result
            assert isinstance(update, Update)
            if not 'message' in update:
                self._log.debug('discarding update {}'.format(update))
                continue
            # Enqueue Message
            message = update['message']
            chat_id = message['chat']['id']
            if chat_id not in self._chats:
                self._log.debug('creating chat {}'.format(chat_id))
                chat = self.message_handler()
                self._chats[chat_id] = chat
            else:
                chat = self._chats[chat_id]
            result = chat.send(message)

    @asyncio.coroutine
    def handle_update(self, update):
        yield from asyncio.sleep(0)
        return self._dispatcher.send(update)
