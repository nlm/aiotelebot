import os
import asyncio
from argparse import ArgumentParser
from .__init__ import TeleBot

@asyncio.coroutine
def start():
    yield 'ok'

def main(arguments=None):
    parser = ArgumentParser()
    parser.add_argument('-T', '--telegram-bot-api-token',
                        default=os.environ.get('TELEGRAM_BOT_API_TOKEN'),
                        help='telegram bot api token')
    parser.add_argument('-d', '--debug',
                        action='store_true', default=False,
                        help='activate debug mode')
    args = parser.parse_args(arguments)

    if args.telegram_bot_api_token is None:
        parser.error('please define TELEGRAM_BOT_API_TOKEN')

    bot = TeleBot(args.telegram_bot_api_token)
    bot.register_command('start', start)

    loop = asyncio.get_event_loop()
    loop.set_debug(args.debug)
    loop.run_until_complete(bot.work())

if __name__ == '__main__':
    main()
