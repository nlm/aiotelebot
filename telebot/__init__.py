import asyncio
import aiohttp
import re
import time
from argparse import ArgumentParser

from .objects import *

class TelegramBotApiError(Exception): pass

class TelegramBotApiClient(object):

    _base_url = 'https://api.telegram.org'

    def __init__(self, token, base_url=None):
        self._token = token
        self._session = aiohttp.ClientSession()
        if base_url is not None:
            self._base_url = base_url

    def __del__(self):
        self._session.close()

    # HTTP Base Methods

    @asyncio.coroutine
    def query(self, http_method, api_method, *args, **kwargs):
        response = yield from self._session.request(http_method,
                                                    '{0}/bot{1}/{2}'
                                                    .format(self._base_url,
                                                            self._token,
                                                            api_method),
                                                    *args, **kwargs)
        try:
            data = yield from response.json()
        except json.JSONDecodeError as exc:
            raise TelegramBotApiError(exc.value)
        return data

    # Telegram API Methods

    def getUpdates(self, update_id, *, timeout=600, limit=100):
        return (yield from self.query('GET', 'getUpdates',
                                      params={'timeout': timeout,
                                              'limit': limit,
                                              'offset': update_id},
                                      timeout=timeout + 5))

class TeleBot(object):

    def __init__(self, token):
        self._client = TelegramBotApiClient(token)
        self._commands = dict()

    def register_command(self, name, coroutine):
        assert asyncio.iscoroutinefunction(coroutine)
        assert re.match('^\w+$', name)
        self._commands[name] = coroutine

    def get_command(self, name):
        return self._commands[name]

    @staticmethod
    def _extract_updates(data):
        if data.get('ok', False) is True:
            for item in data.get('result', []):
                data = object_defaults(TelegramUpdate)
                data.update(item)
                yield TelegramUpdate(**data)

    @asyncio.coroutine
    def watch_updates(self):
        update_id = 0
        last_query = time.time()
        while True:
            print('waiting for an update')
            data = yield from self._client.getUpdates(update_id)
            print('elapsed_time={}'.format(time.time() - last_query))
            for update in self._extract_updates(data):
                print(update)
                #yield from update_handler(update)
                if update.update_id >= update_id:
                    update_id = update.update_id + 1
            #print('update_id = {}'.format(update_id))
            #yield from asyncio.sleep(4)

    @asyncio.coroutine
    def work(self):
        print('in work')
        yield from self.watch_updates()
