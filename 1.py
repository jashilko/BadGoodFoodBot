import telebot
from collections import defaultdict
from telebot import types

token = '2026507498:AAGcuj1jxGjn6poh27UNuseZr3fZfyqs-Kk'

START, PHOTO, RATE, CATEGORY, DESCR, FINISH = range(6)
USER_STATE = defaultdict(lambda: START)


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
        update_state(message, CATEGORY)
    if text == 'canceldescr':
        update_state(message, FINISH)


# Начальное состояние → Просим фото.
@bot.message_handler(func=lambda message: get_state(message) == START)
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Пришли фото')
    update_state(message, PHOTO)


# Состояние: отправлено фото → Просим оценку
@bot.message_handler(func=lambda message: get_state(message) == PHOTO)
@bot.message_handler(content_types=['photo'])
def handle_message(message):
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
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Не хочу', callback_data='canceldescr')
    keyboard.add(b1)
    bot.send_message(chat_id=message.chat.id, text='Добавь описание: ', reply_markup=keyboard)
    update_state(message, FINISH)


bot.polling()
