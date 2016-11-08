import asyncio
from .abc import AsyncBotCore

class TelegramBotCore(AsyncBotCore):

    def __init__(self, bot):
        self.bot = bot

    @asyncio.coroutine
    def handle_update(self, update):
        '''
        Handles an update. Every chat gets a different context,
        therefore a different handler
        '''
        self._log.debug('handle_update')
        if update.message is None:
            self._log.debug('message_is_empty')
            return
        chat_id = update.message['chat']['id']
        if chat_id not in self._chats:
            self._chats[chat_id] = self.update_handler()
            next(self._chats[chat_id])
        update_handler = self._chats[chat_id]
        # XXX: change this ?
        answer = update_handler.send(update.message['text'])
        self._log.debug('ANSWER={} TYPE={}'.format(answer, type(answer)))
        if answer is not None:
            yield from asyncio.sleep(0.5) # safety net
            if isinstance(answer, str):
                yield from self._send_message(chat_id, answer)
            elif isinstance(answer, collections.Iterable):
                for message in answer:
                    yield from self._send_message(chat_id, message)
                    yield from asyncio.sleep(1)
            else:
                self._log.debug('bad answer type: {}'.format(answer))
        else:
            self._log.debug('no answer to send')
