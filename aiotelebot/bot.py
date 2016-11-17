import asyncio
import time
import logging
from .api import TelegramBotApiClient, TelegramBotApiError
from .core import TelegramBotCore


class TelegramBot(object):

    def __init__(self, api_client, core):
        '''
        initializes the bot
        '''
        assert(isinstance(api_client, TelegramBotApiClient))
        assert(isinstance(core, TelegramBotCore))
        self._log = logging.getLogger(__name__)
        self._client = api_client
        self._core = core

    @asyncio.coroutine
    def watch_updates(self):
        '''
        Polls updates from Telegram and handle them
        '''
        update_id = 0
        last_query = time.time()
        throttle = 1
        while True:
            self._log.debug('waiting for updates')
            # API Query
            try:
                result = yield from self._client.getUpdates(update_id=update_id)
                self._log.debug('got result')
            except TelegramBotApiError as err:
                self._log.debug('query error ok={}'.format(result['ok']))
                yield from asyncio.sleep(throttle)
                throttle *= 2
                continue
            self._log.debug('elapsed_time={}'.format(time.time() - last_query))
            last_query = time.time()
            # Checking Result
            if result['ok'] is not True:
                self._log.debug('api returned ok={}'.format(result['ok']))
                yield from asyncio.sleep(throttle)
                throttle *= 2
                continue
            # Extracting Updates
            for update in result['result']:
                self._log.debug('update={}'.format(update))
                yield from self._core.handle_update(update)
                if update['update_id'] >= update_id:
                    update_id = update['update_id'] + 1
            # Success, reset throttling
            throttle = 1

    @asyncio.coroutine
    def work(self):
        '''
        alias to start the bot
        '''
        self._log.info('starting work')
        yield from asyncio.gather(self.watch_updates())

#    @asyncio.coroutine
#    def delayed_answer(messages, delay=1):
#        for message in messages:
#            yield from asyncio.sleep(delay)
#            yield message

