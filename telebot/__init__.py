import asyncio
import aiohttp
import re
import time
import logging
from random import random
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
        logging.debug('doing query {} {}'.format(http_method, api_method))
        response = yield from self._session.request(http_method,
                                                    '{0}/bot{1}/{2}'
                                                    .format(self._base_url,
                                                            self._token,
                                                            api_method),
                                                    *args, **kwargs)
        logging.debug('query {} {} ok'.format(http_method, api_method))
        try:
            logging.debug('decoding response'.format(http_method, api_method))
            data = yield from response.json()
            logging.debug('response ok'.format(http_method, api_method))
        except json.JSONDecodeError as exc:
            raise TelegramBotApiError(exc.value)
        return data

    # Telegram API Methods
    # TODO: enhance these so they return Telegram objects
    # instead of just the json-parsed data

    def getMe(self):
        return (yield from self.query('GET', 'getMe'))

    def getUpdates(self, *, update_id=0, timeout=600, limit=100):
        return (yield from self.query('GET', 'getUpdates',
                                      params={'timeout': timeout,
                                              'limit': limit,
                                              'offset': update_id}))
                                      #timeout=timeout + 5))

    def sendMessage(self, chat_id, text, *, parse_mode=None,
                    disable_web_page_preview=False,
                    disable_notification=False,
                    reply_to_message_id=None, reply_markup=None):
        return (yield from self.query('POST', 'sendMessage',
                                      params={'chat_id': chat_id,
                                              'text': text,
                                              'reply_to_message_id':
                                              reply_to_message_id}))

class TeleBot(object):

    def __init__(self, token):
        self._client = TelegramBotApiClient(token)
        self._commands = dict()
        self._chats = dict()

    def register_command(self, name, coroutine):
        assert asyncio.iscoroutinefunction(coroutine)
        assert re.match('^\w+$', name)
        self._commands[name] = coroutine

    def get_command(self, name):
        return self._commands[name]

    @asyncio.coroutine
    def handle_update(self, update):
        '''
        Handles an update. Every chat gets a different context,
        therefore a different handler
        '''
        print('handle_update')
        chat_id = update.message['chat']['id']
        if chat_id not in self._chats:
            self._chats[chat_id] = self.update_handler()
            next(self._chats[chat_id])
        update_handler = self._chats[chat_id]
        answer = update_handler.send(update.message['text'])
        yield from asyncio.sleep(random() * 2)
        logging.debug('sending answer: {}'.format(answer))
        logging.debug((yield from self._client.sendMessage(chat_id, answer)))

    def update_handler(self):
        context = None
        text = yield
        while True:
            print('handling {}'.format(text))
            try:
                # New command
                if text.startswith('/'):
                    try:
                        cmd_coro = self.get_command(text[1:])
                        if context is not None:
                            context.close()
                        # FIXME: actually incorrect, as we need to handle
                        # command arguments
                        context = cmd_coro()
                        text = yield next(context)
                    except KeyError:
                        text = yield 'unknown command'
                # Followup of an existing command
                elif context is not None:
                    text = yield context.send(text)
                # Text outside a command context
                else:
                    text = yield 'this lacks context'
            except StopIteration:
                print('end of command {}'.format(context))
                context = None
                prompt = None
                #text = yield

    @staticmethod
    def _extract_updates(data):
        if data.get('ok', False) is True:
            for item in data.get('result', []):
                data = object_defaults(TelegramUpdate)
                data.update(item)
                yield TelegramUpdate(**data)

    @asyncio.coroutine
    def watch_updates(self):
        '''
        Polls updates from Telegram and handle them
        '''
        update_id = 0
        last_query = time.time()
        while True:
            logging.debug('waiting for updates')
            data = yield from self._client.getUpdates(update_id=update_id)
            logging.debug('elapsed_time={}'.format(time.time() - last_query))
            last_query = time.time()
            for update in self._extract_updates(data):
                logging.debug('update={}'.format(update))
                yield from self.handle_update(update)
                if update.update_id >= update_id:
                    update_id = update.update_id + 1
            #print('update_id = {}'.format(update_id))
            #yield from asyncio.sleep(4)

    @asyncio.coroutine
    def work(self):
        logging.info('starting work')
        yield from self.watch_updates()
