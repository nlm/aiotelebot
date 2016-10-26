from collections import namedtuple

def object_defaults(obj):
    return {key: None for key in obj._fields}

TelegramUpdate = namedtuple('TelegramUpdate',
                            ['update_id', 'message', 'edited_message',
                             'inline_query', 'chosen_inline_result',
                             'callback_query'])
