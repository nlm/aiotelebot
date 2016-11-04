from parseable import parseable as p, Self, Use, Optional

"""
Definition of Telegram Object Types

from https://core.telegram.org/bots/api#available-types
"""

User = p('User', {'id': int,
                  'first_name': str,
                  Optional('last_name'): str,
                  Optional('user_name'): str})

Chat = p('Chat', {'id': int,
                  'type': str,
                  Optional('title'): str,
                  Optional('username'): str,
                  Optional('first_name'): str,
                  Optional('last_name'): str,
                  Optional('all_members_are_administrators'): bool})

MessageEntity = p('MessageEntity', {'type': str,
                                    'offset': int,
                                    'length': int,
                                    Optional('url'): str,
                                    Optional('user'): Use(User)})

PhotoSize = p('PhotoSize', {'file_id': str,
                            'width': int,
                            'height': int,
                            Optional('file_size'): int})

Audio = p('Audio', {'file_id': str,
                    'duration': int,
                    Optional('performer'): str,
                    Optional('title'): str,
                    Optional('mime_type'): str,
                    Optional('file_size'): int})

Document = p('Document', {'file_id': str,
                          Optional('thumb'): Use(PhotoSize),
                          Optional('file_name'): str,
                          Optional('mime_type'): str,
                          Optional('file_size'): int})

Sticker = p('Sticker', {'file_id': str,
                        'width': int,
                        'height': int,
                        Optional('thumb'): Use(PhotoSize),
                        Optional('emoji'): str,
                        Optional('file_size'): int})

Video = p('Video', {'file_id': str,
                    'width': int,
                    'height': int,
                    'duration': int,
                    Optional('thumb'): Use(PhotoSize),
                    Optional('mime_type'): str,
                    Optional('file_size'): int})

Voice = p('Voice', {'file_id': str,
                    'duration': int,
                    Optional('mime_type'): str,
                    Optional('file_size'): int})

Contact = p('Contact', {'phone_number': str,
                        'first_name': str,
                        Optional('last_name'): str,
                        Optional('user_id'): int})

Location = p('Location', {'longitude': float,
                          'latitude': float})

Venue = p('Venue', {'location': Use(Location),
                    'title': str,
                    'address': str,
                    Optional('foursquare_id'): str})

Animation = p('Animation', {'file_id': str,
                            Optional('thumb'): PhotoSize,
                            Optional('file_name'): str,
                            Optional('mime_type'): str,
                            Optional('file_size'): int})

GameHighScore = p('GameHighScore', {'position': int,
                                    'user': Use(User),
                                    'score': int})

Game = p('Game', {'title': str,
                  'description': str,
                  'photo': [Use(PhotoSize)],
                  Optional('text'): str,
                  Optional('text_entities'): [Use(MessageEntity)],
                  Optional('animation'): Use(Animation)})

CallbackGame = p('CallbackGame', {})

UserProfilePhotos = p('UserProfilePhotos', {'total_count': int,
                                            'photos': [[Use(PhotoSize)]]})

File = p('File', {'file_id': str,
                  Optional('file_size'): int,
                  Optional('file_path'): str})

KeyboardButton = p('KeyboardButton', {'text': str,
                                      Optional('request_contact'): bool,
                                      Optional('request_location'): bool})

ReplyKeyboardHide = p('ReplyKeyboardHide', {'hide_keyboard': bool,
                                            Optional('selective'): bool})

ReplyKeyboardMarkup = p('ReplyKeyboardMarkup',
                        {'keyboard': [[Use(KeyboardButton)]],
                         Optional('resize_keyboard'): bool,
                         Optional('one_time_keyboard'): bool,
                         Optional('selective'): bool})

InlineKeyboardButton = p('InlineKeyboardButton',
                         {'text': str,
                          Optional('url'): str,
                          Optional('callback_data'): str,
                          Optional('switch_inline_query'): str,
                          Optional('switch_inline_query_current_chat'): str,
                          Optional('callback_game'): Use(CallbackGame)})

InlineKeyboardMarkup = p('InlineKeyboardMarkup',
                         {'inline_keyboard': [[Use(InlineKeyboardButton)]]})

InlineQuery = p('InlineQuery', {'id': str,
                                'from': Use(User),
                                Optional('location'): Use(Location),
                                'query': str,
                                'offset': str})


ChosenInlineResult = p('ChosenInlineResult', {'result_id': str,
                                              'from': Use(User),
                                              Optional('location'): Use(Location),
                                              Optional('inline_message_id'): str,
                                              'query': str})


ForceReply = p('ForceReply', {'force_reply': bool,
                              Optional('selective'): bool})

ChatMember = p('ChatMember', {'user': Use(User),
                              'status': str})

ResponseParameters = p('ResponseParameters',
                       {Optional('migrate_to_chat_id'): int,
                        Optional('retry_after'): int})

Message = p('Message', {'message_id': int,
                        Optional('from'): Use(User),
                        'date': int,
                        'chat': Use(Chat),
                        Optional('forward_from'): Use(User),
                        Optional('forward_from_chat'): Use(Chat),
                        Optional('forward_date'): int,
                        Optional('reply_to_message'): Use(Self),
                        Optional('edit_date'): int,
                        Optional('text'): str,
                        Optional('entities'): [Use(MessageEntity)],
                        Optional('audio'): Use(Audio),
                        Optional('document'): Use(Document),
                        Optional('game'): Use(Game),
                        Optional('photo'): [Use(PhotoSize)],
                        Optional('sticker'): Use(Sticker),
                        Optional('video'): Use(Video),
                        Optional('voice'): Use(Voice),
                        Optional('caption'): str,
                        Optional('contact'): Use(Contact),
                        Optional('location'): Use(Location),
                        Optional('venue'): Use(Venue),
                        Optional('new_chat_member'): Use(User),
                        Optional('left_chat_member'): Use(User),
                        Optional('new_chat_title'): str,
                        Optional('new_chat_photo'): [Use(PhotoSize)],
                        Optional('delete_chat_photo'): bool,
                        Optional('group_chat_created'): bool,
                        Optional('supergroup_chat_created'): bool,
                        Optional('channel_chat_created'): bool,
                        Optional('migrate_to_chat_id'): int,
                        Optional('migrate_from_chat_id'): int,
                        Optional('pinned_message'): Use(Self)})

CallbackQuery = p('CallbackQuery',
                  {'id': str,
                   'from': Use(User),
                   Optional('message'): Use(Message),
                   Optional('inline_message_id'): str,
                   Optional('chat_instance'): str,
                   Optional('data'): str,
                   Optional('game_short_name'): str})

Update = p('Update', {'update_id': int,
                      Optional('message'): Use(Message),
                      Optional('edited_message'): Use(Message),
                      Optional('inline_query'): Use(InlineQuery),
                      Optional('chosen_inline_result'): Use(ChosenInlineResult),
                      Optional('callback_query'): Use(CallbackQuery)})

# API Response Objects

APIResponse = p('APIResponse', {'ok': bool,
                                'result': object})

GetUpdatesResponse = p('GetUpdatesReponse', {'ok': bool,
                                             'result': [Update]})

