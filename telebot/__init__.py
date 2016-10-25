import asyncio
import aiohttp
import re

import collections

TelegramUpdate = collections.namedtuple('TelegramUpdate', ['update_id', 'message', 'edited_message', 'inline_query', 'chosen_inline_result', 'callback_query'])

class TelegramBotAPIClient(object):

    _base_url = 'https://api.telegram.org'

    def __init__(self, token, base_url=None):
        self._token = token
        self._session = aiohttp.ClientSession()
        if base_url is not None:
            self._base_url = base_url

    @asyncio.coroutine
    def get(self, method, params=None):
        result = yield from self._session.get('{0}/bot{1}/{2}'
   	                                          .format(self._base_url,
                                                      self._token,
                                                      method),
                                              params=params)
        return result

    @asyncio.coroutine
    def post(self, method, params=None):
        result = yield from self._session.post('{0}/bot{1}/{2}'
   	                                           .format(self._base_url,
                                                       self._token,
                                                       method),
                                               params=params)
        return result

    def getUpdates(self, *, timeout=600, limit=100):
        update_id = 0
        while True:
            response = yield from self._client.get('getUpdates',
                                                   params={'timeout': 600,
                                                           'limit': 100,
                                                           'offset': update_id})

    def __del__(self):
        self._session.close()


class TeleBot(object):

    def __init__(self, token):
        self._client = TelegramBotApiClient(token)
        self._commands = dict()

    def register_command(self, name, coroutine):
        assert asyncio.iscoroutine(coroutine)
        assert re.match('^\w+$', name)
        self._commands[name] = coroutine

    def get_command(self, name):
        return self._commands[name]

    @asyncio.coroutine
    def watch_updates(self):
        update_id = 0
        while True:
            response = yield from self._client.get('getUpdates', params={'timeout': 600,
                                                                         'limit': 100,
                                                                         'offset': update_id})
            try:
                data = yield from response.json()
                update_id = yield from handle_response(data)
            except json.JSONDecodeError:
                text = yield from response.text()
                print('decode error: {}'.format(text))
            yield from asyncio.sleep(2)

    @asyncio.coroutine
    def run_forever(self):
        yield from self._client.watch_updates()



def main():
	pass

if __name__ == '__main__':
	main()
