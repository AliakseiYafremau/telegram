from env_handler import handler
from telebot import TeleBot, types
from os import getenv

handler()


class TelegramBot:
    def __init__(self, token):
        print('[INFO] Initialization of bot')
        self.bot = TeleBot(token)
        print('[INFO] Bot is ready to work')

    def introduction(self, message):
        print('[INFO] Greetings')
        button = types.InlineKeyboardButton(text='Дневник', callback_data='diary')
        markup = types.InlineKeyboardMarkup()
        markup.add(button)
        text = 'Привет, {.first_name}\nМеню:'.format(message.from_user)
        self.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: True)
        def call_handler(call):
            print('[INFO] Running of data handler')
            if call.data == 'diary':
                self.user_page(message)

    def run(self):
        print('[INFO] Running of bot')

        @self.bot.message_handler(commands=['start'])
        def intro(message):
            self.introduction(message)
        self.bot.infinity_polling()

    def user_page(self, message):
        print('[INFO] User_page')
        button_1 = types.InlineKeyboardButton(text='', callback_data='')
        button_1 = types.InlineKeyboardButton(text='', callback_data='')
        button_3 = types.InlineKeyboardButton(text='', callback_data='')
        text = 'Вот ваша страничка\nЧто вы хотите?'
        self.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)



bot = TelegramBot(getenv('TOKEN'))
bot.run()
