from env_handler import handler
from telebot import TeleBot, types
from os import getenv
from helper import info, found
import sqlite3
import helper

handler()


class TelegramBot(TeleBot):
    def introduction(self, message):
        print('[INFO] Introduction ({0})'.format(message.from_user.id))
        button = types.InlineKeyboardButton(text='Дневник', callback_data='diary')
        markup = types.InlineKeyboardMarkup()
        markup.add(button)
        text = 'Привет, {.first_name}\nМеню:'.format(self.client)
        self.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)

    def intro_handler(self, message, call):
        print('[INFO] Running of data handler in Introduction ({0})'.format(message.from_user.id))
        if call.data == 'diary':
            self.user_page(message)
        else:
            self.introduction(message)

    def run(self):
        print('[INFO] Running of bot')
        
        @self.message_handler(commands=['start'])
        def intro(message):
            self.client = message.from_user
            self.introduction(message)
        self.infinity_polling()

    def user_page(self, message):
        print('[INFO] User_page ({0})'.format(message.from_user.id))
        try:
            self.database = sqlite3.connect('database.db')
            self.cursor = self.database.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS user_{0}("
                                "name text,"
                                "grades text)".format(self.client.id))
            print('[INFO] Creating of table of user')
            lessons = info('name', 'user_{0}'.format(self.client.id))
            keyboard = []
            for el in [x[0] for x in lessons]:
                button = types.InlineKeyboardButton(text='Перейти в {0}'.format(el), callback_data='to_{0}'.format(el))
                keyboard.append([button])
            button_1 = types.InlineKeyboardButton(text='Создать урок', callback_data='create')
            button_2 = types.InlineKeyboardButton(text='Вернуться', callback_data='return_to_main')
            keyboard.append([button_1])
            keyboard.append([button_2])
            markup = types.InlineKeyboardMarkup(keyboard=keyboard)
            text = 'Вот ваша страничка\nЧто вы хотите?'
            self.send_message(message.chat.id, text, reply_markup=markup)
        finally:
            self.database.commit()
            self.database.close()

    def user_page_handler(self, message, call):
        print('[INFO] Running of data handler in user_page ({0})'.format(message.from_user.id))
        if call.data == 'return_to_main':
            print(message.text)
            self.introduction(message)
        elif call.data == 'create':
            self.request_of_new_lesson(message)
        else:
            self.lesson_page(message, call.data[3:])

    def request_of_new_lesson(self, message):
        print('[INFO] Creating of lesson')
        self.send_message(message.chat.id, 'Введите название урока')
        self.register_next_step_handler(message, self.create_new_lesson)

    def create_new_lesson(self, message):
        print('[INFO] Attempt to create a new lesson ({0})'.format(message.from_user.id)')
        try:
            self.database = sqlite3.connect('database.db')
            self.cursor = self.database.cursor()
            self.cursor.execute("SELECT COUNT(*) FROM user_{0} WHERE name= '{1}'".format(self.client.id, message.text))
            result = self.cursor.fetchone()
            if result[0] > 0:
                self.send_message(message.chat.id, 'Урок с таким именем уже существует')
            else:
                self.cursor.execute("INSERT INTO user_{0} VALUES {1}".format(self.client.id, (message.text, '')))
                self.send_message(message.chat.id, 'Урок  c именем {0} был создан'.format(message.text))
        except Exception as e:
            print('[ERROR] Create_New_Lesson: ', e)
        finally:
            self.database.commit()
            self.database.close()
        print('[INFO] New lesson was created')
        self.user_page(message)

    def lesson_page(self, message, lesson):
        print('[INFO] Lesson_page ({0})'.format(message.from_user.id))
        try:
            self.database = sqlite3.connect('database.db')
            self.cursor = self.database.cursor()
            self.lessons, self.i = found(lesson, self.client.id)
            av = helper.average(self.lessons[self.i][1])
            if av:
                av_line = f'Ваша средняя оценка: {av}\n'
            else:
                av_line = ''
            text = 'Был выбран урок {0}\n' \
                   'Ваши оценки: {1}\n' \
                    '{2}'\
                   'Что вы хотите?'.format(lesson, helper.str_with_comma(self.lessons[self.i][1]), av_line)
            keyboard = []
            button_1 = types.InlineKeyboardButton('Добавить оценку', callback_data='create_grade')
            keyboard.append([button_1])
            button_2 = types.InlineKeyboardButton('Удалить оценку', callback_data='delete_grade')
            keyboard.append([button_2])
            button_3 = types.InlineKeyboardButton('Удалить урок', callback_data='delete_lesson')
            keyboard.append([button_3])
            button_4 = types.InlineKeyboardButton('Вернуться', callback_data='return_to_user_page')
            keyboard.append([button_4])
            markup = types.InlineKeyboardMarkup(keyboard=keyboard)
            self.send_message(message.chat.id, text, reply_markup=markup)
        finally:
            self.database.commit()
            self.database.close()


    def lesson_page_handler(self, message, call):
        if call.data == 'create_grade':
            self.send_message(message.chat.id, 'Напишите какую оценку вы хотите добавить')
            self.register_next_step_handler(message, self.create_grade, lesson=self.lessons[self.i][0])
        elif call.data == 'delete_grade':
            self.send_message(message.chat.id, 'Напишите какую оценку вы хотите удалить')
            self.register_next_step_handler(message, self.delete_grade, lesson=self.lessons[self.i][0])
        elif call.data == 'delete_lesson':
            self.delete_lesson(message, self.lessons[self.i][0])
        elif call.data == 'return_to_user_page':
            self.user_page(message)

    def create_grade(self, message, lesson):
        try:
            database = sqlite3.connect('database.db')
            cursor = database.cursor()
            old = self.lessons[self.i][1]
            cursor.execute("UPDATE user_{0} SET grades='{1}' WHERE name='{2}'"
                           .format(self.client.id, helper.add_number(old, message.text), lesson))
        finally:
            database.commit()
            database.close()
        self.lesson_page(message, lesson)

    def delete_grade(self, message, lesson):
        try:
            database = sqlite3.connect('database.db')
            cursor = database.cursor()
            old = self.lessons[self.i][1]
            new_value = helper.quit_number(old, message.text)
            if new_value != -1:
                cursor.execute("UPDATE user_{0} SET grades='{1}' WHERE name='{2}'"
                               .format(self.client.id, new_value, lesson))
            else:
                self.send_message(message.chat.id, 'Такой оценки не существует')
        finally:
            database.commit()
            database.close()
        self.lesson_page(message, lesson)

    def delete_lesson(self, message, lesson):
        try:
            database = sqlite3.connect('database.db')
            cursor = database.cursor()
            cursor.execute("DELETE FROM user_{0} WHERE name='{1}'"
                           .format(self.client.id, lesson))
        finally:
            database.commit()
            database.close()
        self.user_page(message)



bot = TelegramBot(getenv('TOKEN'))


@bot.callback_query_handler(func=lambda call: call.data in ['diary'])
def call_handler(call):
    bot.intro_handler(call.message, call)


@bot.callback_query_handler(func=lambda call: call.data in ['create', 'return_to_main'] or call.data[:3] == 'to_')
def user_page_call_handler(call):
    bot.user_page_handler(call.message, call)


@bot.callback_query_handler(func=lambda call: call.data in ['create_grade', 'delete_grade', 'delete_lesson', 'return_to_user_page'])
def lesson_page_handler(call):
    bot.lesson_page_handler(call.message, call)


bot.run()