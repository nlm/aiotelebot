import os
import asyncio
import logging
from argparse import ArgumentParser
from .__init__ import TeleBot

def ticker(interval=1):
    while True:
        print('.', end='', flush=True)
        yield from asyncio.sleep(interval)

@asyncio.coroutine
def start():
    yield 'ok'

@asyncio.coroutine
def hello():
    name = yield 'Hello, what is your name ?'
    yield 'Nice to meet you, {} !'.format(name)

def main(arguments=None):
    parser = ArgumentParser()
    parser.add_argument('-T', '--telegram-bot-api-token',
                        default=os.environ.get('TELEGRAM_BOT_API_TOKEN'),
                        help='telegram bot api token')
    parser.add_argument('-d', '--debug',
                        action='store_true', default=True,
                        help='activate debug mode')
    args = parser.parse_args(arguments)

    if args.telegram_bot_api_token is None:
        parser.error('please define TELEGRAM_BOT_API_TOKEN')

    bot = TeleBot(args.telegram_bot_api_token)
    bot.register_command('start', start)
    bot.register_command('hello', hello)

    loop = asyncio.get_event_loop()
    if args.debug:
        loop.set_debug(True)
        logging.basicConfig(level=logging.DEBUG)
        asyncio.ensure_future(ticker(1))
    loop.run_until_complete(bot.work())

if __name__ == '__main__':
    main()
