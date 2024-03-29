import telebot
import os
import gettext
from flask import Flask, request
from PSQLighter import PSQLighter
from collections import defaultdict
from telebot import types
from SQLAlchemy.controller import DBWorker


# Скачиваем пакет утилит для винды https://mlocati.github.io/articles/gettext-iconv-windows.html
# 1. Запуск xgettext mary.py → Создается файл .po - редактируемый
# 2. Запуск msgfmt mary.po → создается файл .mo - для быстрого чтения программой
# 3. Статья https://phrase.com/blog/posts/translate-python-gnu-gettext/



el = gettext.translation('1', localedir='locales', languages=['ru'])
el.install()
_ = el.gettext


token = os.environ['tg_token']


bot = telebot.TeleBot(token)
server = Flask(__name__)

ZERO, START, PHOTO, RATE, CATEGORY, DESCR, FINISH = range(7)
USER_STATE = defaultdict(lambda: START)

db_worker = PSQLighter()
worker = DBWorker()


# Получаем состояние пользователя
def get_state(message):
    return USER_STATE[message.chat.id]

def set_lang(lang='ru'):
    global el
    global _
    el = gettext.translation('1', localedir='locales', languages=[lang])
    el.install()
    _ = el.gettext

# Устанавливаем состояние пользователя
def update_state(message, state):
    USER_STATE[message.chat.id] = state


# Создаем inline-клавиатуру.
def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton(text='💩' + _(' Shit'), callback_data='shit')
    b2 = types.InlineKeyboardButton(text=_('Amazing ') + ' 😻', callback_data='good')
    keyboard.add(b1, b2)
    return keyboard



# Прислали цифру. Выводим top последних
@bot.message_handler(func=lambda message: message.text.isdigit())
@bot.message_handler(commands=['list'])
def handle_digit(message):
    if message.text.isdigit():
        countt = int(message.text)
    else:
        countt = 5
    #answers = db_worker.get_lasts(message)
    worker.set_user(message.from_user.id)
    answers = worker.get_lasts_from_friends(countt)
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
        score = _(" Score: Amazing ") + "😻" if ans["score"] == 1 else _(" Score: Shit ") + "💩"
        descr = "" if not ans["descr"] else _("Description: ") + ans["descr"]
        cat = "" if not ans["cat"] else _("Category: #") + ans["cat"]
        emo = "" if not ans["foto_link"] else "⬇"
        text = "{}) {};{}{}; User: {}; (id={}) {}".format(str(i), cat, score, descr, ans["first_name"], ans["id"], emo)
        bot.send_message(chat_id=message.chat.id, text=text)
        i += 1
        if ans["foto_link"] is not None:
            bot.send_photo(chat_id=message.chat.id,
                       photo=ans["foto_link"])
        update_state(message, START)

# Прислали тег+тег. Выводим список всех тегов
@bot.message_handler(func=lambda message: message.text == '##')
def handle_allsharp(message):
    worker.set_user(message.from_user.id)
    answers = worker.get_all_tags()
    i = 1
    catlist = ""
    for ans in answers:
        catlist = catlist + ans["cat"] + ", "

    text1 = _("All categories: ") + catlist[:-2]

    bot.send_message(chat_id=message.chat.id, text = text1)
    update_state(message, START)

# Прислали тег. Выводим top 5 последних по тегу
@bot.message_handler(func=lambda message: message.text[0] == '#')
def handle_sharp(message):
    text = _("Display 5 of the latest scores ") + message.text
    bot.send_message(chat_id=message.chat.id, text=text)
    #answers = db_worker.get_sharp(message)
    worker.set_user(message.from_user.id)
    answers = worker.get_sharp_friends(message.text[1:])
    i = 1
    for ans in answers:
        score = _(" Score: Amazing ") + "😻" if ans["score"] == 1 else _(" Score: Shit ") + "💩"
        descr = "" if not ans["descr"] else _("Description: ") + ans["descr"]
        cat = "" if not ans["cat"] else _("Category: #") + ans["cat"]
        emo = "" if not ans["foto_link"] else "⬇"
        text = "{}) {};{}{}; User: {}; (id={}) {}".format(str(i), cat, score, descr, ans["first_name"], ans["id"], emo)
        bot.send_message(chat_id=message.chat.id, text = text)
        i += 1
        if ans["foto_link"] is not None:
            bot.send_photo(chat_id=message.chat.id,
                       photo=ans["foto_link"])
        update_state(message, START)


# Удаление записи по номеру
@bot.message_handler(func=lambda message: message.text[0:2] == '-#')
def handle_sharp(message):
    if db_worker.del_feedback(message) == "Ok":
        text = _("Record №%s deleted") % message.text[2:]
    else:
        text = _("Record №%s don't found in your records") % message.text[2:]
    bot.send_message(chat_id=message.chat.id, text=text)
    update_state(message, START)
    update_state(message, START)


# Обработка нажатия inline-книпки
@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text in ('shit', 'good'):
        text_mes = _("Set the category: ")
        bot.send_message(chat_id=message.chat.id, text=text_mes)
        db_worker.set_score(text)
        update_state(message, CATEGORY)
    if text == 'canceldescr':
        bot.send_message(chat_id=message.chat.id, text='Bye!')
        update_state(message, FINISH)
    if text in "enlang":
        set_lang('en')
        handle_start(message)
    if text in "rulang":
        set_lang('ru')
        handle_start(message)


# Обработка команды /setting
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
def handle_start(message):
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

    keyboard = create_keyboard()
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


if "HEROKU" in list(os.environ.keys()):
    @server.route('/' + token, methods=['POST'])
    def getMessage():
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200


    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://goodbadfood1.herokuapp.com/' + token)
        return "!", 200


    server.run(host="0.0.0.0", port=int(os.environ['PORT']))
else:
     bot.remove_webhook()
     bot.polling()
