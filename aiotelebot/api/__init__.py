from __future__ import absolute_import
import asyncio
import aiohttp
import logging
from .objects import *


class TelegramBotApiError(Exception): pass


class TelegramBotApiClient(object):

    _base_url = 'https://api.telegram.org'

    def __init__(self, token, base_url=None):
        self._token = token
        self._session = aiohttp.ClientSession()
        self._log = logging.getLogger(__name__)
        if base_url is not None:
            self._base_url = base_url

    def __del__(self):
        self._session.close()

    # HTTP Base Methods

    @asyncio.coroutine
    def query(self, http_method, api_method, *args, **kwargs):
        self._log.debug('doing query {} {}'.format(http_method, api_method))
        response = yield from self._session.request(http_method,
                                                    '{0}/bot{1}/{2}'
                                                    .format(self._base_url,
                                                            self._token,
                                                            api_method),
                                                    *args, **kwargs)
        self._log.debug('query {} {} ok'.format(http_method, api_method))
        try:
            self._log.debug('decoding response'.format(http_method, api_method))
            data = yield from response.json()
            self._log.debug('response ok'.format(http_method, api_method))
        except json.JSONDecodeError as exc:
            raise TelegramBotApiError(exc.value)
        return data

    # Telegram API Methods
    # TODO: enhance these so they return Telegram objects
    # instead of just the json-parsed data

    @asyncio.coroutine
    def getMe(self):
        data = yield from self.query('GET', 'getMe')
        return GetMeResponse(data)

    @asyncio.coroutine
    def getUpdates(self, *, update_id=0, timeout=600, limit=100):
        data = yield from self.query('GET', 'getUpdates',
                                      params={'timeout': timeout,
                                              'limit': limit,
                                              'offset': update_id})
        return GetUpdatesResponse(data)

    @asyncio.coroutine
    def sendMessage(self, chat_id, text, *, parse_mode=None,
                    disable_web_page_preview=False,
                    disable_notification=False,
                    reply_to_message_id=None, reply_markup=None):
        return (yield from self.query('POST', 'sendMessage',
                                      params={'chat_id': chat_id,
                                              'text': text,
                                              'reply_to_message_id':
                                              reply_to_message_id}))

