import asyncio
import re
import time
import logging
import inspect
import collections
from random import random
from .api.objects import *
from .api import TelegramBotApiClient, TelegramBotApiError


class TeleBot(object):

    def __init__(self, token):
        self._log = logging.getLogger(__name__)
        self._client = TelegramBotApiClient(token)
        self._commands = dict()
        self._chats = dict()
        self._help = dict()
        self._log.debug('self-registering')
        for name, function in self._get_commands():
            self.register_command(name, function)
        self._log.debug('end self-registering')
        self._log.debug(self._help)

    def _get_commands(self):
        for key, value in inspect.getmembers(self, inspect.isgeneratorfunction):
            if re.match('cmd_\w+$', key):
                yield (key.replace('cmd_', ''), value)

    def register_command(self, name, generator):
        assert inspect.isgeneratorfunction(generator)
        assert re.match('^\w+$', name)
        self._log.debug('registering command {} -> {}'.format(name, generator))
        self._commands[name] = generator
        self._help[name] = inspect.getdoc(generator)

    def register_default_command(self, generator):
        assert inspect.isgeneratorfunction(generator)
        self._commands['__default__'] = generator

    def cmd_help(self, args):
        """
        get help about functions
        """
        return '\n'.join(['Sure! Here\'s what i can do:', ''] +
                         ['/{} - {}'.format(func, doc or '(no description)')
                          for func, doc in sorted(self._help.items())
                          if not (func.startswith('_') or func in ('start', 'stop'))])
        yield

    def get_command(self, name):
        return self._commands[name]

    def update_handler(self):
        context = None
        text = yield
        while True:
            self._log.debug('handling text "{}" (context={})'.format(text, context))
            try:
                # New command
                if text.startswith('/'):
                    try:
                        cmd_gen = self.get_command(text[1:])
                        args = text.split()[1:]
                        if context is not None:
                            context.close()
                        context = cmd_gen(args)
                        text = yield next(context)
                    except KeyError:
                        text = yield 'unknown command'
                # Followup of an existing command
                elif context is not None:
                    self._log.debug('sending {} in context {}'.format(text, context))
                    text = yield context.send(text)
                # Text outside a command context
                else:
                    try:
                        cmd_gen = self.get_command('__default__')
                        args = text.split()
                        context = cmd_gen(args)
                        text = yield next(context)
                    except KeyError:
                        text = yield
            except StopIteration as stopiter:
                self._log.debug('end of command {}'.format(context))
                context = None
                text = yield stopiter.value

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

    @asyncio.coroutine
    def _send_message(self, chat_id, message):
        self._log.debug('sending message {}'.format(message))
        return (yield from self._client.sendMessage(chat_id, message))

    @staticmethod
    def _extract_updates(data):
        if data.get('ok', False) is True:
            for item in data.get('result', []):
                yield Update(item).data

#    @asyncio.coroutine
#    def delayed_answer(messages, delay=1):
#        for message in messages:
#            yield from asyncio.sleep(delay)
#            yield message

    @asyncio.coroutine
    def watch_updates(self):
        '''
        Polls updates from Telegram and handle them
        '''
        update_id = 0
        last_query = time.time()
        while True:
            self._log.debug('waiting for updates')
            data = yield from self._client.getUpdates(update_id=update_id)
            self._log.debug('elapsed_time={}'.format(time.time() - last_query))
            last_query = time.time()
            for update in self._extract_updates(data):
                self._log.debug('update={}'.format(update))
                yield from self.handle_update(update)
                if update.update_id >= update_id:
                    update_id = update.update_id + 1
            #print('update_id = {}'.format(update_id))
            #yield from asyncio.sleep(4)

    @asyncio.coroutine
    def work(self):
        self._log.info('starting work')
        yield from self.watch_updates()
