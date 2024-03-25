from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import *
import data
from threading import Thread
import sqlite3
import YaGPT
persons = ["Мадам Аврора", "Капитан Кракен", "Принцесса Зария", "Мастер Тай", "Мое имя", "Свой вариант, сейчас напишу"]
location = ["Затерянный город", "Остров Забытых Душ", "Подземелье Времен", "Москва"]
bot = TeleBot(TOKEN)
users = {}

"""
ВАРИАНТ ДОСТОЙНЫЙ ФИНАЛЬНОГО ПРОЕКТА!!!
"""
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    t2 = Thread(target=data.prepare_database())
    t1 = Thread(target=data.prepare_second_database())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот, который поможет тебе сгенерировать историю🐍!"
                          f"Я работаю бок о бок с YaGPT🤖👾. Удачного использования!)"
                        "Если вы намерены продолжить историю, напишите продолжение, если нет - /stop",
                     reply_markup=create_keyboard(["/new_history", '/help']))

@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "тут пока ничего нет")

@bot.message_handler(commands=["new_history"])
def complexity(message):
    bot.send_message(message.chat.id, "Выберите жанр):\n/fantasy - фантастика\n/comedy - комедия\n/novel - роман.", reply_markup=create_keyboard(["/fantasy", "/comedy", "/novel"]))

@bot.message_handler(commands=["stop"])
def stop(message):
    give_end_prompt_get_answer(message)

@bot.message_handler(commands=["fantasy"])
def fantasy(message):
    t2 = Thread(target=data.add_gener(id=message.chat.id, genre='фантастика'))
    t1 = Thread(target=ask_about_name(message))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

@bot.message_handler(commands=["comedy"])
def comedy(message):
    t2 = Thread(target=ask_about_name(message))
    t1 = Thread(target=data.add_gener(id=message.chat.id, genre='комедия'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

@bot.message_handler(commands=["novel"])
def novel(message):
    t2 = Thread(target=ask_about_name(message))
    t1 = Thread(target=data.add_gener(id=message.chat.id, genre='роман'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

def ask_about_name(message):
    a = data.is_limit_users_in_prompt_table()
    """
    Небольшая проверка на колличество пользователей, после первого вброса данных о них
    """
    if a:
        bot.register_next_step_handler(message, hwo_are_you)
        bot.send_message(message.chat.id, "Выбирете персонажа:", reply_markup=create_keyboard(
            [persons[0], persons[1], persons[2], persons[3], persons[4], persons[5]]))
    else:
        bot.send_message(message.chat.id, "Кажется кто-то влез без очереди, вы не можете пройти дальше, пользователей много")
        bot.stop_bot()
def hwo_are_you(message):
    if message.text == persons[0]:
        name = persons[0]
        write_name(name, message)
    elif message.text == persons[1]:
        name = persons[1]
        write_name(name, message)
    elif message.text == persons[2]:
        name = persons[2]
        write_name(name, message)
    elif message.text == persons[3]:
        name = persons[3]
        write_name(name, message)
    elif message.text == persons[4]:
        name = message.chat.id
        write_name(name, message)
    elif message.text == persons[5]:
        bot.send_message(message.chat.id, "Введите имя):")
        bot.register_next_step_handler(message, your_name)
    else:
        bot.send_message(message.chat.id, "Начните процедуру сначала видимо что-то пошло не так")
        delete_story_of_prompt_generation(message)
        bot.register_next_step_handler(message, start)
def your_name(message):
    name = message.text
    data.add_name(id=message.chat.id, name=name)
    location_of_person(message)
def write_name(name, message):
    t2 = Thread(target=location_of_person(message))
    t1 = Thread(target=data.add_name(id=message.chat.id, name=name))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
def location_of_person(message):
    bot.register_next_step_handler(message, place_of_man)
    bot.send_message(message.chat.id, "Выбирете сеттинг:", reply_markup=create_keyboard(
        [location[0], location[1], location[2], location[3]]))
def place_of_man(message):
    if message.text == location[0]:
        write_place(message, place=location[0])
    elif message.text == location[1]:
        write_place(message, place=location[1])
    elif message.text == location[2]:
        write_place(message, place=location[2])
    elif message.text == location[3]:
        write_place(message, place=location[3])
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так")
        delete_story_of_prompt_generation(message)
        bot.register_next_step_handler(message, start)
def write_place(message, place):
    do_it = True
    t2 = Thread(target=data.add_place(id=message.chat.id, place=place))
    t1 = Thread(target=create_prompt(message=message, do_it=do_it))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
def create_prompt(message,do_it):
    if do_it:
        what_session(message)
    print(users[message.chat.id])
    if message.chat.id in users:
        if users[message.chat.id] < 3:
            bot.send_message(message.chat.id, "Ожидайте ответа, скоро вы его обязательно получите!\n Это вам не ЖИВЫЕ ОЧЕРЕДИ В LM STUDIO!")
            text = preparation_for_generation(id=message.chat.id)
            tokens_of_prompt_or_answer = YaGPT.count_tokens(prompt_or_answer=text)
            t2 = Thread(target=data.start_regestration_for_people(message, text=text, tokens_of_prompt_or_answer=tokens_of_prompt_or_answer, session_ID=users[message.chat.id]))
            t1 = Thread(target=give_prompt_get_answer(message, text))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
def give_prompt_get_answer(message, text):
    answer = YaGPT.ask_gpt(text=text)
    bot.send_message(message.chat.id, answer)
    tokens_of_prompt_or_answer = YaGPT.count_tokens(prompt_or_answer=answer)
    t2 = Thread(target=data.start_regestration_for_assistent(message, text=answer, tokens_of_prompt_or_answer=tokens_of_prompt_or_answer, session_ID=users[message.chat.id]))
    t1 = Thread(target=message_for_start_addition_prompt(message))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
def message_for_start_addition_prompt(message):
    bot.register_next_step_handler(message ,addition_promt)
def addition_promt(message):
    if message.text != "/stop" and message.text != "/clear":
        addition = message.text
        text = preporation_for_addition(addition)
        tokens_of_prompt_or_answer = YaGPT.count_tokens(prompt_or_answer=text)
        t2 = Thread(target=data.start_regestration_for_people(message, text=text, tokens_of_prompt_or_answer=tokens_of_prompt_or_answer, session_ID=users[message.chat.id]))
        t1 = Thread(target=give_prompt_get_answer(message, text))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
def preparation_for_generation(id):
    connection = sqlite3.connect('for_text.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT name, place, gener FROM promt WHERE id = {id};')
    for res in results:
        name = res[0]
        place = res[1]
        gener = res[2]
    text = f"{SYSTEM_PROMPT}, главный герой - {name}, место - {place}, история в жанре {gener}"
    return text
def preporation_for_addition(addition):
    for_story = ""
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT content FROM questions WHERE role = "assistent";')
    for res in results:
        for_story += str(res)
    text = f"{CONTINUE_STORY}, не обращай внимание на скопки и не пиши их в ответе, вот история: {str(for_story)}, {addition};"
    return text

def preporation_for_end_generation(message):
    for_story = ()
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT content FROM questions WHERE user_id = {message.chat.id} and role = "assistent";')
    for res in results:
        for_story += res
    text = f"{END_STORY}, вот истоия которую нужно дополнить, не обращай внимание на скобки и не пиши их в ответе: {for_story}"
    tokens_of_prompt_or_answer = YaGPT.count_tokens(prompt_or_answer=text)
    data.start_regestration_for_people(message, text=text, tokens_of_prompt_or_answer=tokens_of_prompt_or_answer,
                                          session_ID=users[message.chat.id])
    return text
def give_end_prompt_get_answer(message):
    text = preporation_for_end_generation(message=message)
    answer = YaGPT.ask_gpt(text=text)
    bot.send_message(message.chat.id, answer)
    tokens_of_prompt_or_answer = YaGPT.count_tokens(prompt_or_answer=answer)
    data.start_regestration_for_assistent(message, text=answer, tokens_of_prompt_or_answer=tokens_of_prompt_or_answer, session_ID=users[message.chat.id])
    delete_story_of_prompt_generation(message)
def delete_story_of_prompt_generation(message):
    connection = sqlite3.connect('for_text.db')
    cur = connection.cursor()
    cur.execute(f"DELETE FROM promt WHERE id = {message.chat.id}")
    connection.commit()
    connection.close()
def session_id(message):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    session = cur.execute(f"SELECT session_ID FROM questions WHERE user_id = {message.chat.id}")
    for i in session:
        what = i[-1]
        return int(what)

def what_session(message):
    session_if_start = 0
    what = session_id(message)
    if what is not None:
        if users[message.chat.id] == 2:
            bot.send_message(message.chat.id,
                             "Что-то пошло не так, либо две сессии были завершены! К сожалению вы не можете продолжать пользоваться услугами бота :(")
            users[message.chat.id] = 3
            block(message=message)
        elif users[message.chat.id] == 1:
            bot.send_message(message.chat.id, "Это ваша последняя сессия! Удачки)")
            session_ID = 2
            users[message.chat.id] = 2
            return session_ID
        else:
            bot.send_message(message.chat.id,
                             "Что-то пошло не так, либо две сессии были завершены! К сожалению вы не можете продолжать пользоваться услугами бота :(")
            users[message.chat.id] = 3
            block(message)
    else:
        users[message.chat.id] = session_if_start + 1
        session_ID = session_if_start + 1
        return session_ID

def block(message):
    pass

bot.polling()

