import telebot
import os
import gettext
from PSQLighter import PSQLighter
from collections import defaultdict
from telebot import types


# Скачиваем пакет утилит для винды https://mlocati.github.io/articles/gettext-iconv-windows.html
# 1. Запуск xgettext mary.py → Создается файл .po - редактируемый
# 2. Запуск msgfmt mary.po → создается файл .mo - для быстрого чтения программой
# 3. Статья https://phrase.com/blog/posts/translate-python-gnu-gettext/


el = gettext.translation('1', localedir='locales', languages=['ru'])
el.install()

_ = el.gettext

token = os.environ['tg_token']

ZERO, START, PHOTO, RATE, CATEGORY, DESCR, FINISH = range(7)
USER_STATE = defaultdict(lambda: START)

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
    b1 = types.InlineKeyboardButton(text='💩 ' + _('Shit'), callback_data='shit')
    b2 = types.InlineKeyboardButton(text=_('Amazing') + ' 😻', callback_data='good')
    keyboard.add(b1, b2)
    return keyboard


bot = telebot.TeleBot(token)

# Прислали цифру. Выводим top последних
@bot.message_handler(func=lambda message: message.text.isdigit())
@bot.message_handler(commands=['list'])
def handle_digit(message):
    if message.text.isdigit():
        countt = int(message.text)
    else:
        countt = 5
    answers = db_worker.get_lasts(message)
    if len(answers) == 0:
        text = _('No records in the database')
    elif message.text.isdigit():
        if countt > len(answers):
            text = _('There are only %d scores') % (len(answers))
        else:
            text = _('Display %s of the latest scores: ') % (message.text)

    else:
        text = _('Display %s of the latest scores. For another count, write a number: ') % len(answers)

    bot.send_message(chat_id=message.chat.id, text=text)

    i = 1
    for ans in answers:
        if ans["score"] == 1:
            score = _(" Score: Amazing ")
        elif ans["score"] == -1:
            score = _(" Score: Shit ")
        else:
            score = " "
        if ans["descr"] is None:
            descr = ""
        else:
            descr = _("Description: ") + ans["descr"]
        if ans["cat"] is None:
            cat = " "
        else:
            cat = _("Category: #") + ans["cat"]
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
        update_state(message, START)


# Прислали тег. Выводим top 5 последних по тегу
@bot.message_handler(func=lambda message: message.text[0] == '#')
def handle_sharp(message):
    text = _("Display 5 of the latest scores ") + message.text
    bot.send_message(chat_id=message.chat.id, text=text)
    answers = db_worker.get_sharp(message)
    i = 1
    for ans in answers:
        if ans["score"] == 1:
            score = _(" Score: Amazing ")
        elif ans["score"] == -1:
            score = _(" Score: Shit ")
        else:
            score = " "
        if ans["descr"] is None:
            descr = ""
        else:
            descr = _("Description: ") + ans["descr"]
        if ans["cat"] is None:
            cat = " "
        else:
            cat = _("Category: #") + ans["cat"]
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
        update_state(message, START)

# Обработка нажатия inline-книпки
@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text in ('shit', 'good'):
        text = _("Set the category: ")
        bot.send_message(chat_id=message.chat.id, text=text)
        db_worker.set_score(text)
        update_state(message, CATEGORY)
    if text == 'canceldescr':
        bot.send_message(chat_id=message.chat.id, text='Bye!')
        update_state(message, FINISH)

@bot.message_handler(commands=['setting'])
def handle_message(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    entext = 'English ' + '🇺🇸'
    rutext = 'Русский ' + '🇷🇺'
    b1 = types.InlineKeyboardButton(text=entext, callback_data='enlang')
    b2 = types.InlineKeyboardButton(text=rutext, callback_data='rulang')
    keyboard.add(b1, b2)
    text = _("Let's set a language: ")
    bot.send_message(chat_id=message.chat.id, text=text,
                     reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def handle_message(message):
    update_state(message, START)
    text = _("Upload a photo or write a name")
    bot.send_message(chat_id=message.chat.id, text=text)
    update_state(message, PHOTO)

@bot.message_handler(commands=['help'])
def handle_message(message):
    help_en = _("Upload a photo of the food and give an assessment. \n The bot will remember and show what is good and what is not. \n Write a number to output so many recent scores.\n Write \"#coffee\" to get the last 5 entries about coffee")
    bot.send_message(chat_id=message.chat.id, text=help_en)

# Начальное состояние → Просим фото.
@bot.message_handler(func=lambda message: get_state(message) == START)
def handle_message(message):
    text = _("Upload a photo or write a name")
    bot.send_message(chat_id=message.chat.id, text=text)
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
    shittext = '💩' + ''
    goottext = 'Amazing ' + '😻'
    b1 = types.InlineKeyboardButton(text=shittext, callback_data='shit')
    b2 = types.InlineKeyboardButton(text=goottext, callback_data='good')
    keyboard.add(b1, b2)
    text = _('Estimate the food. There is no average score, only bad or good')
    bot.send_message(chat_id=message.chat.id, text=text,
                     reply_markup=keyboard)
    update_state(message, RATE)

# Состояние: отправлена оценка → Просим категорию
@bot.message_handler(func=lambda message: get_state(message) == RATE)
def handle_message(message):
    text = _("Set the category: ")
    bot.send_message(chat_id=message.chat.id, text=text)
    update_state(message, CATEGORY)


# Состояние: установлена категория → Просим описание
@bot.message_handler(func=lambda message: get_state(message) == CATEGORY)
def handle_message(message):
    # Обработка категории.
    db_worker.set_category(message)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    notext = _("Not want")
    b1 = types.InlineKeyboardButton(text=notext, callback_data='canceldescr')
    keyboard.add(b1)
    text = _('Category #%s is set. Do you want to add something to the description?') % message.text
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)
    update_state(message, DESCR)


# Устанавливаем описание.
@bot.message_handler(func=lambda message: get_state(message) == DESCR)
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Bye')
    db_worker.set_descr(message)
    update_state(message, FINISH)


@bot.message_handler(commands=['setting'])
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Coming soon')


bot.polling()
