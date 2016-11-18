import asyncio
import logging
import inspect
import re
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from .api.objects import Update

TelegramChat = namedtuple('TelegramChat', ['queue', 'handler'])

class TelegramBotCore(object, metaclass=ABCMeta):

    default_queue_size = 10

    def __init__(self, api_client):
        self.api_client = api_client
        self._dispatcher = self.dispatcher()
        self._dispatcher.send(None)
        self._chats = {}
        self._log = logging.getLogger(__name__)

    @abstractmethod
    @asyncio.coroutine
    def message_handler(self, queue):
        return NotImplementedError

    def create_queue(self, maxsize=None):
        '''
        Create a new queue

        :param maxsize: the maximum size of the queue
        :return: the new queue object
        '''
        if maxsize is None:
            maxsize = self.default_queue_size
        return asyncio.Queue(maxsize)

    @asyncio.coroutine
    def dispatcher(self):
        while True:

            # Obtain Update
            update = yield
            assert isinstance(update, Update)

            # Filter the incoming update types
            # TODO: add more message handling cases
            if not 'message' in update:
                self._log.debug('discarding update {}'.format(update))
                continue

            # Get Chat object
            message = update['message']
            chat_id = message['chat']['id']
            if chat_id not in self._chats:
                self._log.debug('creating chat {}'.format(chat_id))
                queue = self.create_queue()
                handler = self.message_handler(queue)
                task = asyncio.ensure_future(handler)
                chat = TelegramChat(queue, task)
                self._chats[chat_id] = chat
            else:
                chat = self._chats[chat_id]

            # Wait if queue is full
            while chat.queue.full():
                self._log.warning('queue is full for chat_id {}'.format(chat_id))
                yield from asyncio.sleep(1)

            # Enqueue the message
            chat.queue.put_nowait(message)

    @asyncio.coroutine
    def handle_update(self, update):
        self._dispatcher.send(update)
        yield from asyncio.sleep(0)


class TelegramBotCommandCore(TelegramBotCore):

    def __init__(self, api_client):
        TelegramBotCore.__init__(self, api_client)
        self._log = logging.getLogger(__name__)
        # Init Commands
        self._commands = {}
        self._help = {}
        for name, function in self.get_commands():
            self.register_command(name, function)

    def _extract_command(self, text):
        if not text.startswith('/'):
            return (None, None)
        parts = (text.split()[0][1:]).split('@', maxsplit=1)
        if len(parts) > 1:
            return parts
        else:
            return (parts[0], None)

    @asyncio.coroutine
    def message_handler(self, queue):
        context = None
        me = (yield from self.api_client.getMe())['result']
        self._log.debug(me)
        while True:
            message = yield from queue.get()
            self._log.info('handling {}'.format(message))
            text = message.get('text')
            if text is None:
                self._log.debug('no text in message')
                continue
            chat_id = message['chat']['id']

            try:
                # New command
                if text.startswith('/'):
                    try:
                        cmd, target = self._extract_command(text)
                        self._log.debug('command={}, target={}'.format(cmd, target))
                        if target is not None and target != me.get('username', None):
                            self._log.debug('not a target for command {}'.format(cmd))
                            continue
                        self._log.debug('command lookup: {}'.format(cmd))
                        cmd_gen = self.get_command(cmd)
                        args = text.split()[1:]
                        if context is not None:
                            self._log.debug('closing existing context: {}'.format(context.__name__))
                            context.close()
                        context = cmd_gen(args)
                        self._log.debug('starting new context: {}'.format(context.__name__))
                        yield from self.api_client.sendMessage(chat_id, next(context))
                    except KeyError:
                        yield from self.api_client.sendMessage(chat_id, 'unknown command')
                # Followup of an existing command
                elif context is not None:
                    self._log.debug('sending {} in context {}'.format(text, context))
                    yield from self.api_client.sendMessage(chat_id, context.send(text))
                # Text outside a command context
                else:
                    try:
                        cmd_gen = self.get_command('__default__')
                        args = text.split()
                        context = cmd_gen(args)
                        yield from self.api_client.sendMessage(chat_id, next(context))
                    except KeyError:
                        self._log.debug('no default command defined, discarding message')
            except StopIteration as stopiter:
                self._log.debug('end of context: {}'.format(context.__name__))
                context = None
                yield from self.api_client.sendMessage(chat_id, stopiter.value)

	# Commands Part

    def get_commands(self):
        for key, value in inspect.getmembers(self, inspect.isgeneratorfunction):
            if re.match('cmd_\w+$', key):
                yield (key.replace('cmd_', ''), value)

    def get_command(self, name):
        return self._commands[name]

    def register_command(self, name, generator):
        assert inspect.isgeneratorfunction(generator)
        assert re.match('^\w+$', name)
        self._log.debug('registering command {} -> {}'.format(name, generator))
        self._commands[name] = generator
        self._help[name] = inspect.getdoc(generator)

    def register_default_command(self, generator):
        assert inspect.isgeneratorfunction(generator)
        self._commands['__default__'] = generator

	# Pre-defined commands

    @asyncio.coroutine
    def cmd_help(self, args):
        '''
        get help about this bot commands
        '''
        return '\n'.join(['Sure! Here\'s what i can do:', ''] +
                         ['/{} - {}'.format(func, doc or '(no description)')
                          for func, doc in sorted(self._help.items())
                          if not (func.startswith('_') or func in ('start', 'stop'))])
        yield
