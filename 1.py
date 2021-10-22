import telebot
import os
from PSQLighter import PSQLighter
from collections import defaultdict
from telebot import types

token = os.environ['tg_token']

ZERO, START, PHOTO, RATE, CATEGORY, DESCR, FINISH = range(7)
USER_STATE = defaultdict(lambda: ZERO)

db_worker = PSQLighter()

# Получаем состояние пользователя
def get_state(message):
    return USER_STATE[message.chat.id]


# Устанавливаем состояние пользователя
def update_state(message, state):
    USER_STATE[message.chat.id] = state


# Создаем inline-клавиатуру.
def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton(text='💩' + ' Говно', callback_data='shit')
    b2 = types.InlineKeyboardButton(text='Охуенно ' + '😻', callback_data='good')
    keyboard.add(b1, b2)
    return keyboard


bot = telebot.TeleBot(token)


# Обработка нажатия inline-книпки
@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text in ('shit', 'good'):
        bot.send_message(chat_id=message.chat.id, text='Укажи категорию: ')
        db_worker.set_score(text)
        update_state(message, CATEGORY)
    if text == 'canceldescr':
        bot.send_message(chat_id=message.chat.id, text='Bye!')
        update_state(message, FINISH)

@bot.message_handler(commands=['start'])
def handle_message(message):
    update_state(message, START)
    bot.send_message(chat_id=message.chat.id, text='Пришли фото или название')
    update_state(message, PHOTO)

# Начальное состояние → Просим фото.
@bot.message_handler(func=lambda message: get_state(message) == START)
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Пришли фото')
    update_state(message, PHOTO)


# Состояние: отправлено фото → Просим оценку
@bot.message_handler(func=lambda message: get_state(message) == PHOTO)
@bot.message_handler(content_types=['photo'])
def handle_message(message):
    # Проверка пользователя на существование
    db_worker.check_exist_client(message.chat)
    # Пользователь прислал описание или фото
    if message.content_type == 'photo':
        db_worker.set_photo(message)
    else:
        db_worker.set_descr(message)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton(text='💩' + ' Говно', callback_data='shit')
    b2 = types.InlineKeyboardButton(text='Охуенно ' + '😻', callback_data='good')
    keyboard.add(b1, b2)
    bot.send_message(chat_id=message.chat.id, text='Оцени еду. Средней оценки нет, только плохо или хорошо',
                     reply_markup=keyboard)
    update_state(message, RATE)


# Состояние: отправлена оценка → Просим категорию
@bot.message_handler(func=lambda message: get_state(message) == RATE)
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Укажи категорию: ')
    update_state(message, CATEGORY)


# Состояние: установлена категория → Просим описание
@bot.message_handler(func=lambda message: get_state(message) == CATEGORY)
def handle_message(message):
    # Обработка категории.
    db_worker.set_category(message)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Не хочу', callback_data='canceldescr')
    keyboard.add(b1)
    bot.send_message(chat_id=message.chat.id, text='Категория #' + message.text +
                                                   ' установлена. Хочешь что-то добавить к описанию?', reply_markup=keyboard)
    update_state(message, DESCR)


# Устанавливаем описание.
@bot.message_handler(func=lambda message: get_state(message) == DESCR)
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Bye')
    db_worker.set_descr(message)
    update_state(message, FINISH)

# Прислали цифру. Выводим top последних
@bot.message_handler(func=lambda message: message.text.isdigit())
@bot.message_handler(commands=['list'])
def handle_digit(message):
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Вывожу ' + message.text + ' последних оценок')
    else:
        bot.send_message(chat_id=message.chat.id, text='Вывожу 5 последних оценок. Для другого количества напиши цифру')
    answers = db_worker.get_lasts(message)
    i = 1
    for ans in answers:
        if ans["score"] == 1:
            score = " Оценка: Охуенно "
        elif ans["score"] == -1:
            score = " Оценка: Говно "
        else:
            score = " "
        if ans["descr"] is None:
            descr = ""
        else:
            descr = "Описание: " + ans["descr"]
        if ans["cat"] is None:
            cat = " "
        else:
            cat = "Категория: #" + ans["cat"]
        if ans["foto_link"] is not None:
            emo = '⬇'
        else:
            emo = ''
        text = str(i) + ") " + cat + score + descr + "(id=" + str(ans["id"]) + ")" + emo
        bot.send_message(chat_id=message.chat.id, text=text)
        i += 1
        if ans["foto_link"] is not None:
            bot.send_photo(chat_id=message.chat.id,
                       photo=ans["foto_link"])




# Прислали тег. Выводим top 5 последних по тегу
@bot.message_handler(func=lambda message: message.text[0] == '#')
def handle_sharp(message):
    bot.send_message(chat_id=message.chat.id, text='Вывожу 5 последних ' + message.text)
    answers = db_worker.get_sharp(message)
    i = 1
    for ans in answers:
        if ans["score"] == 1:
            score = " Оценка: Охуенно "
        elif ans["score"] == -1:
            score = " Оценка: Говно "
        else:
            score = " "
        if ans["descr"] is None:
            descr = ""
        else:
            descr = "Описание: " + ans["descr"]
        if ans["cat"] is None:
            cat = " "
        else:
            cat = "Категория: #" + ans["cat"]
        if ans["foto_link"] is not None:
            emo = '⬇'
        else:
            emo = ''
        text = str(i) + ") " + cat + score + descr + "(id=" + str(ans["id"]) + ")" + emo
        bot.send_message(chat_id=message.chat.id, text = text)
        i += 1
        if ans["foto_link"] is not None:
            bot.send_photo(chat_id=message.chat.id,
                       photo=ans["foto_link"])

@bot.message_handler(commands=['setting'])
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Coming soon')

@bot.message_handler(commands=['help'])
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Кидай фото еды и давай оценку. Бот запомнит и покажет, что хорошо, а что нет')


bot.polling()
