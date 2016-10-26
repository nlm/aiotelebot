import os
import asyncio
import logging
from argparse import ArgumentParser
from .__init__ import TeleBot

class DemoBot(TeleBot):

    def cmd_start(self, args):
        return "Let's go !"

    def cmd_notgenerator(self):
        pass

    def cmd_hello(self, args):
        name = yield 'Hello, what is your name ?'
        return 'Nice to meet you, {} !'.format(name)

    def cmd_cancel(self, args):
        return 'ok, canceled'
        yield # hack to make this a generator

def ticker(interval=1):
    while True:
        print('.', end='', flush=True)
        yield from asyncio.sleep(interval)

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

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    if args.debug:
        loop.set_debug(True)
        asyncio.ensure_future(ticker(1))

    bot = DemoBot(args.telegram_bot_api_token)
    loop.run_until_complete(bot.work())

if __name__ == '__main__':
    main()
