import sqlite3
import telebot
import config
bot = telebot.TeleBot(config.TOKEN)
"""
Будет 2 таблици, первая - для общения с нееростетью, вторая - для формирования текста промта.
"""


"""
ПЕРВАЯ ТАБЛИЦА ДЛЯ ОБЩЕНИЯ С НЕЕРОСЕТЬЮ.
"""
def prepare_database():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()

    query = (f'CREATE TABLE IF NOT EXISTS questions' \
                    f'(id INTEGER AUTO_INCREMENT PRIMARY KEY, ' \
                    f'user_id INTEGER, ' \
                    f'name TEXT, ' \
                    f'role TEXT, ' \
                    f'content TEXT, ' \
                    f'tokens INTEGER, ' \
                    f'session_ID INTEGER)')

    cur.execute(query)
    connection.commit()
    cur.close()

def start_regestration_for_people(message, text, tokens_of_prompt_or_answer, session_ID):
    id = message.from_user.id
    name = message.from_user.first_name
    role = "user"
    content = text
    tokens = tokens_of_prompt_or_answer
    session = session_ID
    first_info = (id, name, role, content, tokens, session)
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute(
        f'INSERT INTO questions (user_id, name, role, content, tokens, session_ID) VALUES (?, ?, ?, ?, ?, ?);', first_info)
    connection.commit()
    cur.close()

def start_regestration_for_assistent(message, text, tokens_of_prompt_or_answer, session_ID):
    id = message.from_user.id
    name = message.from_user.first_name
    role = "assistent"
    content = text
    tokens = tokens_of_prompt_or_answer
    session = session_ID
    first_info = (id, name, role, content, tokens, session)
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute(
        f'INSERT INTO questions (user_id, name, role, content, tokens, session_ID) VALUES (?, ?, ?, ?, ?, ?);', first_info)
    connection.commit()
    cur.close()

def for_people_prompt(text, id):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute('UPDATE questions SET content = "{}" WHERE id= {} and role = "user"'.format(text, id))
    connection.commit()
    connection.close()

def for_assistent_prompt(text, id):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute("UPDATE questions SET content = '{}' WHERE id= {} and role = {}".format(text, id, "assistent"))
    connection.commit()
    connection.close()

"""
ВТОРАЯ ТАБЛИЦА ДЛЯ ФОРМИРОВАНИЯ ТЕКСТА ПРОМТА.
"""
def prepare_second_database():
    connection = sqlite3.connect('for_text.db')
    cur = connection.cursor()

    query = (f'CREATE TABLE IF NOT EXISTS promt' \
                    f'(id INTEGER PRIMARY KEY, ' \
                    f'name TEXT, ' \
                    f'place TEXT, ' \
                    f'gener TEXT)')
    cur.execute(query)
    connection.commit()
    cur.close()

def add_gener(id, genre):
    connection = sqlite3.connect('for_text.db')
    cur = connection.cursor()
    first_info = (id, genre)
    cur.execute(
        f'INSERT INTO promt (id, gener) VALUES (?, ?);', first_info)
    connection.commit()
    cur.close()

def add_place(id, place):
    connection = sqlite3.connect('for_text.db')
    cur = connection.cursor()
    cur.execute("UPDATE promt SET place = '{}' WHERE id= {}".format(place, id))
    connection.commit()
    connection.close()

def add_name(id, name):
    connection = sqlite3.connect('for_text.db')
    cur = connection.cursor()
    cur.execute("UPDATE promt SET name = '{}' WHERE id= {}".format(name, id))
    connection.commit()
    connection.close()

def add_text(id, text):
    connection = sqlite3.connect('for_text.db')
    cur = connection.cursor()
    cur.execute("UPDATE promt SET text = '{}' WHERE id= {}".format(text, id))
    connection.commit()
    connection.close()


"""
ДРУГИЕ ФУНКЦИИ С ИСПОЛЬЗОВАНИЕМ БАЗЫ ДАННЫХ!
"""

def is_limit_users_in_prompt_table():
    connection = sqlite3.connect('for_text.db')
    cursor = connection.cursor()
    result = cursor.execute('SELECT DISTINCT id FROM promt;')
    count = 0
    for i in result:
        count += 1
    connection.close()
    if count > config.MAX_USERS:
        a = False
    else:
        a = True
    return a

def count_tokens_in_in_session(id, session, message):
    count = 0
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    results = cursor.execute(f'SELECT tokens FROM questions WHERE id = {id} and session_ID = {session};')
    for result in results:
        count += result
    if count >= config.MAX_TOKENS_IN_SESSION:
        bot.send_message(message.chat.id, "Похоже вы израсходоваоли все токены в сессии, прошу начните сначала создавать историю /new_story")
    elif count + 50 >= config.MAX_TOKENS_IN_SESSION:
        bot.send_message(message.chat.id, "У вас осталось мало токенов, в районе 50, прора бы закругляться /stop")
    elif count  == config.MAX_TOKENS_IN_SESSION / 2:
         bot.send_message(message.chat.id, "У вас осталась половина токенов в сессии, будьте спокойны)")

def count_tokens_in_project(message):
    count = 0
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    results = cursor.execute(f'SELECT tokens FROM questions WHERE id = {message.chat.id};')
    for result in results:
        count += result
    if count >= config.MAX_PROJECT_TOKENS / 2:
        bot.send_message(message.chat.id, "Вы израсходовали все токены, доступ к боту закрыт!")
        bot.stop_bot()




