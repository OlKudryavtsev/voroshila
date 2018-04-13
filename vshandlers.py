#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,KeyboardButton, ParseMode
import logging
from functools import wraps
from emoji import emojize
import time
import datetime
import random
from tabulate import tabulate

import os, fnmatch
import re
import apiai
import json

from vsfunc import *

SELECT, TEAM, MATCH = range(3)
KEYBOARD, KEYBOARDECHO, ARCHIVE, ARCHIVEECHO = range(4)

HELP_SYNONYMS = ["помоги!", "помоги", "на помощь", "help!", "help", "что умеешь", "как выполнить?", "?", "⚠помощь"]
WINNER_SYNONYMS = ["кто победил?", "кто победил", "покажи победителей", "покажи чемпионов", "winners", "champion",
                   "победители", "чемпионы", "🏆все победители"]
TABLE_SYNONYMS = ["таблица", "покажи таблицу", "результаты", "итог", "📅итоги турнира вс2017"]
LINK_SYNONYMS = ["ссылка", "ссылки", "где посмотреть", "googledocs", "docs", "➕результаты матчей"]
TEAMS_SYNONYMS = ["кто участвует?", "кто участвует", "участники", "кто зарегистрировался?", "кто зарегистрировался",
                  "команды", "покажи команды", "⚽список участников"]
REGLAMENT_SYNONUMS = ["📝регламент турнира", "регламент", "покажи регламент", "как играем"]

BASIC_MENU = ["1", "2", "3", "4", "5", "6"]
YEARS = ["2017", "2018"]

LIST_OF_ADMINS = [230308082, 186972507]
#LIST_OF_ADMINS = [230308082]
# Список победителей прошлых турниров
WINNERS = {
    '2012': 'Вадим Швецов',
    '2013': 'Вадим Швецов',
    '2015': 'Олег Кудрявцев',
    '2016': 'Дмитрий Самойлов',
    '2017': 'Александр Шевченко'
}

# Ссылки на google docs таблицы турниров
DOCLINKS = {
    '2018': 'https://docs.google.com/spreadsheets/d/1fRioNQwo5jFWS26egaVE9HwyNgZFn9qj376vr8mjdKo/edit#gid=1211524932',
    '2017': 'https://docs.google.com/spreadsheets/d/1OCN01o6SvG8PDTakbKm8TFQ4kU9HMCgWnRTbTfmjBdw/edit#gid=1211524932'
}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# функция для ограничения доступа к вызовам хандлеров. СТавить @restricted перед нужной функцией (def ...)
def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        chat_id = update.message.chat_id
        #if update.effective_user:
        #    user_id = update.effective_user.id
        if chat_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(chat_id))
            bot.send_message(chat_id=chat_id, text="К сожалению, у тебя нет прав на выполнение данной команды ✋️")
            return
        return func(bot, update, *args, **kwargs)

    return wrapped


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    # chat_id = bot.get_updates()[-1].message.chat_id

    try:
        chat_id = bot.get_updates()[-1].message.chat_id
    except IndexError:
        chat_id = update.message.chat_id
    if update.message.from_user.first_name:
        first_name = update.message.from_user.first_name
    else:
        first_name = ""
    if update.message.from_user.last_name:
        last_name = update.message.from_user.last_name
    else:
        last_name = ""
    insertnewuser(chat_id, first_name, last_name)
    bot.send_message(chat_id=230308082,
                     text="Зарегистрирован новый пользователь: " + update.message.from_user.first_name + " " + update.message.from_user.last_name)
    update.message.reply_text('Привет, {}!'.format(update.message.from_user.first_name))
    update.message.reply_text('Тебя приветствует официальный бот турнира Ворошиловский стрелок ⚽️👍!')
    keyboard(bot, update)
    # update.message.reply_text('Чтобы посмотреть, что я умею, напиши /help')


def help(bot, update):
    """Send a message when the command /help is issued."""
    #text = "Смотри, что я умею:"
    #text += "\n/teamlist - получить список зарегистрировшихся участников"
    #text += "\n/reglament - показать регламент турнира ВС2018"
    #text += "\n/winners - показать список победителей прошлых турниров"
    #text += "\n/links - показать ссылки на GoogleDocs"
    #text += "\n/table2017 - показать турнирную таблицу ВС2017"
    #text += "\n/msgto - написать сообщение определенному контакту"
    #text += "\nвсем: текст сообщения - написать сообщение всем пользователям"
    #text += "\n\nА еще ты можешь мне просто писать 'победители','помощь','покажи таблицу' и т.д."
    text = """
Выбери на клавиатуре⌨, что тебя интересует.
Вот что я уже знаю и умею 🤓
"""
    update.message.reply_text(text)
    time.sleep(1)
    text = """
По текущему турниру:
⚽Список участников
📝Регламент турнира
🗓Турнирная таблица
🔜Ближайшие 5️⃣ матчей
🔜Запланированные матчи
🎥Видео матчей
"""
    update.message.reply_text(text)
    time.sleep(1)
    text = """
Также есть 📅Архив, где ты можешь посмотреть:
🏆Все победители
📅Турнирная таблица ВС2017
Результаты матчей
"""
    update.message.reply_text(text)
    time.sleep(1)
    text = """
Если ты участник турнира, то ❗обязательно❗️пользуйся следующими функциями:
👋🏽Готов! / 🚷Не готов
⭕Свои оставшиеся матчи
✅Свои сыгранные матчи
"""
    update.message.reply_text(text)



# функция, показывающая список зарегистрировавшихся команд
def teamlist(bot, update):
    """Send a message when the command /teamlist is issued."""
    TEAMS = getteaminfo()
    teamlist = ""
    i = 0
    for team in TEAMS:
        i = i + 1
        teamlist = teamlist + "\n" + team[2] + "\t" + team[3] + "\t" + team[1]
    update.message.reply_text('Количество зарегистрировавшихся участников - ' + str(i))
    update.message.reply_text('Список участников:\n' + teamlist)


# функция, показывающая список победителей прошлых турниров
def winners(bot, update):
    """Send a message when the command /winners is issued."""
    # chat_id = update.message.chat_id
    winnerlist = ""
    for winner in WINNERS:
        winnerlist = winnerlist + "\nВС" + winner + ": \t" + WINNERS[winner]
    # bot.send_message(chat_id=chat_id, text='Победители турнира:\n' + winnerlist)
    update.message.reply_text('Победители турнира:\n' + winnerlist)


# функция вывода текущего регламента турнира
def reglament(bot, update):
    """Send a message when the command /reglament is issued."""
    reglament_text = "В разработке"
    REGLAMENT = """
Система: сезон, 11 команд, 1 круг.
По итогам групп состоятся 2 розыгрыша плейофф - основная сетка и сетка "лузеров".
1 место "регулярки" сразу выходит в полуфинал.
2-7 места образуют ТРИ пары 1/4 плейофф (2-7, 3-6, 4-5).
8-11 места образуют два полуфинала сетки "лузеров" (8-11, 9-10).

Суммарное количество игр в сезоне - 65 (55 регулярка, 7 основной плейофф, 3 - "лузеров").

Призы "регулярки":
1 место - 1000р
2-3 места - по 500р
4-7 места - по 250р

Призы "чемпионата":
🥇 - 3000р
🥈 - 2000р
🥉 - 1000р
🏆 сетки "лузеров" - 1000р

Старт турнира: 28.01.2018.

P.S. Регламент может быть пересмотрен к концу лета в случае, если травмированные игроки не смогут продолжить свое участие в турнире.
    """
    update.message.reply_text(REGLAMENT)


# функция показа турнирной таблицы по итогам 2017 года
def table2017(bot, update):
    """Send a message when the command /table2017 is issued."""
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=open('C:/ВС/ВС2017_table.png', 'rb'))


# функция отбражения ссылок на google docs всех турниров
def links(bot, update):
    """Send a message when the command /links is issued."""
    links = ""
    for year in DOCLINKS:
        links = links + "\nВС" + year + ": \t" + DOCLINKS[year]
    update.message.reply_text(links)


# функция отбражения ссылки на google docs турнира выбранного года (year)
def link(bot, update, year):
    """Send a message when the command /links is issued."""
    links = ""
    links = DOCLINKS[year]
    update.message.reply_text(links)


# функция - обработчки всего, кроме текста
def echonotext(bot, update):
    """Echo the user message."""
    print("We in echonotext")
    sender_chat_id = update.message.chat_id
    chat_ids, firstnames, fullnames = getchatids()
    i = 0
    if update.message.video:
        video_id = update.message.video.file_id
        bot.send_message(chat_id=230308082,
                         text='<b>' + update.message.from_user.first_name + " " + update.message.from_user.last_name + '</b> FILE_ID = : ' + video_id,
                         parse_mode=ParseMode.HTML)
        bot.send_video(chat_id = 230308082, video=video_id)
    for chat_id, name in zip(chat_ids, fullnames):
        i = i + 1
        if update.message.photo:
            photo = update.message.photo[-1]
            bot.send_message(chat_id=chat_id,
                             text='<b>' + update.message.from_user.first_name + " " + update.message.from_user.last_name + '</b>',
                             parse_mode=ParseMode.HTML)
            bot.send_photo(chat_id=chat_id, photo=photo)
        if update.message.sticker:
            sticker = update.message.sticker
            bot.send_message(chat_id=chat_id,
                             text='<b>' + update.message.from_user.first_name + " " + update.message.from_user.last_name + '</b>',
                             parse_mode=ParseMode.HTML)
            bot.send_sticker(chat_id=chat_id, sticker=sticker)
        #if update.message.location:
            #longitude = update.message.location.longitude
            #latitude = update.message.location.latitude
            #bot.send_message(chat_id=chat_id,
            #                 text='<b>' + update.message.from_user.first_name + " " + update.message.from_user.last_name + '</b>',
            #                 parse_mode=ParseMode.HTML)
            #bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)
        if update.message.venue:
            longitude = update.message.venue.location.longitude
            latitude = update.message.venue.location.latitude
            title = update.message.venue.title
            address = update.message.venue.address
            bot.send_venue(chat_id=chat_id, latitude=latitude, longitude=longitude, title = title, address = address)
    msginsert(sender_chat_id, '', msg)


# функция, вызывающая нужный метод исходя из текста запроса
def echo(bot, update):
    """Echo the user message."""
    # update.message.reply_text(update.message.text)
    print("We in echo")
    echotext = update.message.text
    echotext = echotext.lower()

    if echotext in HELP_SYNONYMS:
        help(bot, update)
    elif echotext in WINNER_SYNONYMS:
        winners(bot, update)
    elif echotext in TABLE_SYNONYMS:
        table2017(bot, update)
    elif echotext in LINK_SYNONYMS:
        links(bot, update)
    elif echotext in TEAMS_SYNONYMS:
        teamlist(bot, update)
    elif echotext in REGLAMENT_SYNONUMS:
        reglament(bot, update)
    else:
        sendmessage(bot, update)
        #apiaicall(bot, update)

def apiaicall(bot, update):
    request = apiai.ApiAI('f6c3e3934c0e4bb083775d3d2dc9a2ec').text_request()  # Токен API к Dialogflow
    request.lang = 'ru'  # На каком языке будет послан запрос
    request.session_id = 'VoroshilaBot'  # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.query = update.message.text  # Посылаем запрос к ИИ с сообщением от юзера
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech']  # Разбираем JSON и вытаскиваем ответ
    # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
    if response:
        bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Я Вас не совсем понял!')


# функция для отправки пожелания администраторам
def mywish(bot, update, args):
    msg = ""
    for arg in args:
        msg = msg + " " + arg
    with open('wishes/wishes.txt', 'a') as w_file:
        w_file.write(update.message.from_user.first_name + " " + update.message.from_user.last_name + ": " + msg + "\n")
    bot.send_message(chat_id=230308082,
                     text=update.message.from_user.first_name + " " + update.message.from_user.last_name + ": " + msg)
    update.message.reply_text('Спасибо! Твое мнение очень важно для нас!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


# функция создания меню-клавиатуры
def keyboard(bot, update):
    #    custom_keyboard = [["🏆Все победители", "⚽Список участников"],
    #                       ["➕Результаты матчей", "📝Регламент турнира"],
    #                       ["✏Отправить сообщение", "📅Итоги турнира ВС2017"],
    #                       ["⚠Помощь"]]
    chat_id = update.message.chat_id
    chat_ids, firstnames, fullnames = getvschatids()
    text = "Выбери, что тебя интересует"
    custom_keyboard = [["🔛Результаты матчей", "🔜Ближайшие матчи"],
                       ["🎥Видео матчей"],
                       ["⚽Список участников", "📝Регламент турнира"],
                       ["📅Архив"],
                      #["✏Отправить сообщение"],
                       ["🕹Управление"]]
    if str(chat_id) in chat_ids:
        is_answer = answaboutready(chat_id, str(getnextsunday()))
        is_ready = isready(chat_id, str(getnextsunday()), True)
        is_not_ready = isready(chat_id, str(getnextsunday()), False)

        if is_answer == 0:
            rdy = ["👋🏽Готов!", "🚷Не готов"]
        elif is_ready:
            rdy = ["🚷Отменить готовность"]
        elif is_not_ready:
            rdy = ['👋🏽Готов!']
        custom_keyboard.insert(0,rdy)
        text = text + "\n" + "Не забывай указывать свою готовность (👋🏽Готов!, 🚷Не готов) играть в ближайшее воскресенье!"
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text(text, reply_markup=reply_markup)


# функция выбора года (надо заменить на беседу)
def yearchoise(bot, update):
    keyboard = [[InlineKeyboardButton("2️⃣0️⃣1️⃣7️⃣", callback_data='2017'),
                 InlineKeyboardButton("2️⃣0️⃣1️⃣8️⃣", callback_data='2018')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Выбери год:', reply_markup=reply_markup)


def sendmessage_regex(bot, update):
    """Send a message when the command /sendmessage is issued."""
    sender_chat_id = update.message.chat_id
    msg = re.sub(r'(всем|Всем|ВСЕМ):\s+', '', update.message.text, re.I)
    chat_ids, firstnames, fullnames = getchatids()
    i = 0
    for chat_id, name in zip(chat_ids, fullnames):
        i = i + 1
        bot.send_message(chat_id=chat_id, text=update.message.from_user.first_name + " " + update.message.from_user.last_name + ":\n" + msg)
    msginsert(sender_chat_id, '', msg)

def sendmessage(bot, update):
    """Send a message when the command /sendmessage is issued."""
    sender_chat_id = update.message.chat_id
    #msg = re.sub(r'(всем|Всем|ВСЕМ):\s+', '', update.message.text, re.I)
    msg = update.message.text
    chat_ids, firstnames, fullnames = getchatids()
    i = 0
    for chat_id, name in zip(chat_ids, fullnames):
        i = i + 1
        if str(chat_id) == str(sender_chat_id):
            pass
            #print(str(chat_id) + "; " + str(sender_chat_id))
            #bot.send_message(chat_id=chat_id, text='<b>' + update.message.from_user.first_name + " " + update.message.from_user.last_name + '</b>' + ":\n" + msg, parse_mode=ParseMode.HTML)
        else:
            #print(str(chat_id) + "; " + str(sender_chat_id))
            bot.send_message(chat_id=chat_id,
                             text='<b>' + update.message.from_user.first_name + " " + update.message.from_user.last_name + '</b>' + ":\n" + msg,
                             parse_mode=ParseMode.HTML)
    msginsert(sender_chat_id, '', msg)

def msgto(bot, update, args):
    """Send a message when the command /msgto is issued."""
    sender_chat_id = update.message.chat_id
    if not args:
        msg_help = """
Для отправки сообщения пользователю напишите '/msgto user_id Текст сообщения'. Например, '/msgto 230308082 Привет, Олег!'
"""
        msg_users = """
        На данный момент можно написать следующим пользователям (user_id - первый столбец):\n
"""
        chat_ids, firstnames, fullnames = getchatids()
        for chat_id, name in zip(chat_ids, fullnames):
            msg_users = msg_users + chat_id + "\t\t" + name + "\n"
        update.message.reply_text(msg_help)
        time.sleep(2)
        update.message.reply_text(msg_users)
    else:
        msg = ""
        j = 0
        chat_id = args[0]

        for arg in args:
            if j > 0:
                msg = msg + " " + arg
            j = j + 1
        bot.send_message(chat_id=chat_id, text=msg)
        msginsert(sender_chat_id, chat_id, msg)


def archive(bot, update):
    reply_keyboard = [["🏆Все победители", "📅Турнирная таблица ВС2017"],
                      ['Результаты матчей'], ["🔙Назад"]]

    update.message.reply_text(
        '👇🏽',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def cancel(bot, update):
    bot.sendMessage(update.message.chat_id, "Bye!")
    return ConversationHandler.END


@restricted
def shuffle(bot, update):
    teams = getteamlist('2018')
    dicteam = {}
    diclist = ""
    # chat_ids = [230308082, 186972507]
    # fullnames = ["Олег", "Alex"]
    chat_ids, firstnames, fullnames = getchatids()
    for chat_id, name in zip(chat_ids, fullnames):
        bot.send_message(chat_id=chat_id,
                         text=name + ", через несколько секунд начнется жеребьевка турнира Ворошиловский стрелок 2018!")
        time.sleep(2)
        bot.send_message(chat_id=chat_id,
                         text="Напоминаю, что календарь матчей уже составлен, но не определены номера участников.")
    time.sleep(6)
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text="Итак... стартуем!")
    time.sleep(2)
    for item, team in zip(random.sample(range(1, 11), 10), teams):
        dicteam[item] = team
        time.sleep(1)
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text="Вытаскиваю номер для команды " + team + "...")
            # update.message.reply_text("Итак, выберем номер для команды " + team[0])
        time.sleep(12)
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text="Команда получает номер: " + str(item) + "!")
        time.sleep(8)
        # update.message.reply_text("Команда получает номер: " + str(item))

    for key, value in sorted(dicteam.items()):
        diclist = diclist + "\nКоманда" + str(key) + ":\t\t" + dicteam[key]
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text="Итоговые номера команд:\t\t" + diclist)


def keyboardecho(bot, update):
    """Echo the user message."""
    sender_chat_id = update.message.chat_id
    print("We in keyboardecho")
    chat_ids, firstnames, fullnames = getvschatids()
    chat_id = update.message.chat_id
    echotext = update.message.text
    queryinsert(sender_chat_id, echotext)
    # echotext = echotext.lower()
    if echotext == "⚽Список участников":
        teamlist(bot, update)

    elif echotext == "📝Регламент турнира":
        reglament(bot, update)

    elif echotext == "🎥Видео матчей":
        showgamevideo(bot, update)

    elif echotext == "📅Архив":
        archive(bot, update)

    elif echotext == "✏Отправить сообщение":
        msgto(bot, update, "")

    elif echotext == "⚠Помощь":
        help(bot, update)

    elif echotext == "🏆Все победители":
        winners(bot, update)
        archive(bot, update)

    elif echotext == "📅Турнирная таблица ВС2017":
        table2017(bot, update)
        archive(bot, update)

    elif echotext == "Результаты матчей":
        teams(bot, update)
        # archive(bot, update)

    elif echotext in getteamlist('2017'):
        chat_id = update.message.chat_id
        matches = getmatchschedule(echotext, '2017', '', 1)
        match_text = ""
        for match in matches:
            match_text = match_text + "\n" + str(match[4]) + ":\t\t" + str(match[0]) + " " + str(
                match[2]) + " - " + str(match[3]) + " " + str(match[1])
        update.message.reply_text(match_text)
        archive(bot, update)

    elif echotext == "🔙Назад":
        keyboard(bot, update)

    elif echotext == "🔚Назад":
        archive(bot, update)

    elif echotext == "🔜Ближайшие 5️⃣ матчей":
        next5games(bot, update)
        if str(chat_id) not in chat_ids:
            notvsplayersmenu(bot, update)
        else:
            gamecalendar(bot, update)

    elif echotext == "🔜Ближайшие матчи":
        chat_id = update.message.chat_id
        plannedgames(bot, update)
        if str(chat_id) not in chat_ids:
            notvsplayersmenu(bot, update)
        else:
            gamecalendar(bot, update)

    elif echotext == "🔜Запланированные матчи":
        chat_id = update.message.chat_id
        plannedgames(bot, update)
        if str(chat_id) not in chat_ids:
            notvsplayersmenu(bot, update)
        else:
            gamecalendar(bot, update)

    elif echotext == "🔛Результаты матчей":
        gameresults(bot, update)
        games_menu(bot, update)
        time.sleep(5)
        if str(chat_id) not in chat_ids:
            notvsplayersmenu(bot, update)
        else:
            gameresult(bot, update)

    elif echotext == "👋🏽Готов!":
        ready2play(bot, update, True)
        gamecalendar(bot, update)

    elif echotext == "🚷Не готов":
        ready2play(bot, update, False)
        gamecalendar(bot, update)

    elif echotext == "🚷Отменить готовность":
        ready2play(bot, update, False)
        gamecalendar(bot, update)

    elif echotext == "⭕Свои оставшиеся матчи":
        chat_id = str(update.message.chat_id)
        yourteam = getyourteam(chat_id, 2018)
        if yourteam:
            update.message.reply_text("Тебе предстоит сыграть следующие матчи:")
            time.sleep(1)
            matches = getmatchschedule(yourteam, '2018', '', 0)
            match_text = ""
            for match in matches:
                match_text = match_text + "\n" + str(match[0]) + str(match[6]) + " - " + str(match[7]) + str(match[1])
            update.message.reply_text(match_text)
        gamecalendar(bot, update)

    elif echotext == "✅Свои сыгранные матчи":
        chat_id = str(update.message.chat_id)
        yourteam = getyourteam(chat_id, 2018)
        if yourteam:
            update.message.reply_text("Результаты твоих сыгранных матчей:")
            time.sleep(1)
            matches = getmatchschedule(yourteam, '2018', '', 1)
            if len(matches) > 0:
                match_text = ""
                for match in matches:
                    date = str(match[4]) + ": "
                    match_text = match_text + "\n" + str(date) + str(match[0]) + str(match[6]) + " " + str(match[2]) + " - " + str(match[3]) + " " + str(match[7]) + str(match[1])
            else:
                match_text = "Ты еще не сыграл ни одной игры 😳"
            update.message.reply_text(match_text)
        gamecalendar(bot, update)

    elif echotext == "🗓Турнирная таблица":
        showtable(bot,update)
        if str(chat_id) not in chat_ids:
            notvsplayersmenu(bot, update)
        else:
            gameresult(bot, update)

    elif echotext == "🕹Управление":
        if chat_id in LIST_OF_ADMINS:
            adminkey(bot, update)
        else:
            update.message.reply_text("⛔Данный раздел доступен только организаторам!")

    elif echotext == "👻️Кто готов?":
        if chat_id in LIST_OF_ADMINS:
            whoisready(bot, update, True)

    elif echotext == "🛌️Кто не готов?":
        if chat_id in LIST_OF_ADMINS:
            whoisready(bot, update, False)

    elif echotext == "🤼‍♀Готовые пары":
        if chat_id in LIST_OF_ADMINS:
            showpossiblegames(bot, update)
            #possiblegames(bot, update)

    elif echotext == "Назначить матч📅 или внести результат⚽":
        if chat_id in LIST_OF_ADMINS:
            set(bot, update, None)

    elif echotext == "Внести результат матча⚽":
        if chat_id in LIST_OF_ADMINS:
            showplannedgames(bot, update)


    else:
        echo(bot, update)

# функция создания списка команд
def teams(bot, update):
    chat_id = str(update.message.chat_id)
    yourteam = getyourteam(chat_id, 2017)
    if yourteam:
        update.message.reply_text("О! Я смотрю, ты уже участвовал в турнире ВС 🏁.\nВот результаты твоих матчей:")
        time.sleep(1)
        matches = getmatchschedule(yourteam, '2017', '', 1)
        match_text = ""
        for match in matches:
            match_text = match_text + "\n" + str(match[4]) + ":\t\t" + str(match[0]) + " " + str(
                match[2]) + " - " + str(match[3]) + " " + str(match[1])
        update.message.reply_text(match_text)
    teams = getteamlist('2017')
    teams_keyboard = []
    teams_1 = []
    teams_2 = []
    teams_3 = []
    teams_keyboard = [teams_1, teams_2, teams_3, ["🔚Назад"]]
    i = 0
    for team in teams:
        if i < 4:
            teams_1.append(team)
        elif i > 3 and i < 8:
            teams_2.append(team)
        else:
            teams_3.append(team)
        i = i + 1
    reply_markup = ReplyKeyboardMarkup(teams_keyboard, one_time_keyboard=True)
    time.sleep(2)
    update.message.reply_text('Можешь посмотреть результаты матчей другой команды либо вернуться назад:',
                              reply_markup=reply_markup)

def plannedgames(bot, update):
    date = getnextsunday()
    matches = getplannedgames()
    if len(matches) == 0:
        next5games(bot, update)
    else:
        match_text = ""
        for match in matches:
            if match[7]:
                date_text = str(match[7]) + ": "
            else:
                date_text = ""
            match_text = match_text + "\n" + date_text + str(match[1]) + str(
                match[3]) + " - " + str(match[6]) + str(match[4]) + " " + ". Тур " + str(match[8])
        update.message.reply_text("На ближайшее воскресенье запланировано проведение следующих матчей:")
        time.sleep(1)
        update.message.reply_text(match_text)
        time.sleep(1)

def gamecalendar(bot, update):
    chat_id = update.message.chat_id
    is_answer = answaboutready(chat_id, str(getnextsunday()))
    is_ready = isready(chat_id, str(getnextsunday()), True)
    is_not_ready = isready(chat_id, str(getnextsunday()), False)
    if is_answer == 0:
        reply_keyboard = [["👋🏽Готов!", "🚷Не готов", ],
                          ["🔜Ближайшие 5️⃣ матчей"],
                          ["⭕Свои оставшиеся матчи", "✅Свои сыгранные матчи"],
                          ["🔙Назад"]]
        text = "‼️Обязательно‼️\nЕсли ты Готов играть в ближайшее воскресенье " + str(getnextsunday()) + ", жми 👋🏽Готов!\nЕсли нет - жми 🚷Не готов"
    elif is_ready > 0:
        reply_keyboard = [["🚷Отменить готовность"],
                          ["🔜Ближайшие 5️⃣ матчей"],
                          ["⭕Свои оставшиеся матчи", "✅Свои сыгранные матчи"],
                          ["🔙Назад"]]
        text = "Также можешь посмотреть 👇🏽"
    elif is_not_ready > 0:
        reply_keyboard = [['👋🏽Готов!'],
                          ["🔜Ближайшие 5️⃣ матчей"],
                          ["⭕Свои оставшиеся матчи", "✅Свои сыгранные матчи"],
                          ["🔙Назад"]]
        text = 'Если ты готов сыграть в ближайшее воскресенье ' + str(getnextsunday()) + ', жми 👋🏽Готов!'
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def notvsplayersmenu(bot, update):
    reply_keyboard = [["🗓Турнирная таблица", "🔛Результаты матчей"],
                      ["🔜Ближайшие 5️⃣ матчей", "🔜Запланированные матчи"],
                          ["🔙Назад"]]
    text = "Эх, жаль, что ты не принимаешь участие в турнире..."
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def gameresult(bot, update):
    print("we in gameresult")
    chat_id = update.message.chat_id
    reply_keyboard = [["🗓Турнирная таблица"],
                          ["⭕Свои оставшиеся матчи", "✅Свои сыгранные матчи"],
                          ["🔙Назад"]]
    text = "Также можешь посмотреть 👇🏽"

    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def gameresults(bot, update):
    matches = getmatchschedule('', '2018', 5, 1)
    match_text = ""
    for match in matches:
        date = ""
        if match[4]:
            date = str(match[4]) + ": "
        match_text = match_text + "\n" + str(date) + str(match[0]) + str(match[6]) + " " + str(match[2]) + " - " + str(
            match[3]) + " " + str(match[7]) + str(match[1])
    update.message.reply_text("Последние 5️⃣  сыгранных матчей:")
    time.sleep(1)
    update.message.reply_text(match_text)
    time.sleep(1)

#all games calendar. Added 19.03.2018
def games_menu(bot, update):
    keyboard_list = [
                     InlineKeyboardButton("Посмотреть полный календарь", callback_data="full_calendar")
                     ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard_list, n_cols=1), resize_keyboard=True)
    update.message.reply_text('Также можешь посмотреть 👇🏽', reply_markup=reply_markup)

def allgames(bot, update):
    matches = getmatchschedule(None, '2018', None, None)
    i = 1
    match_text = "Тур 1"
    for match in matches:

        #update.message.reply_text(match_text)
        team_one_name = match[0]
        team_two_name = match[1]
        team_one_goals = match[2]
        team_two_goals = match[3]
        game_date = match[4]
        game_tour = match[5]
        team_one_emoji = match[6]
        team_two_emoji = match[7]

        if i == game_tour:
            date = ""
            if game_date:
                date = ". " + str(game_date)
            if team_one_goals:
                match_text = match_text + "\n✅" + str(team_one_name) + str(team_one_emoji) + " " + str(team_one_goals) + " - " \
                             + str(team_two_goals) + " " + str(team_two_emoji) + str(team_two_name) + str(date)
            else:
                match_text = match_text + "\n⭕" + str(team_one_name) + str(team_one_emoji) + " - " + str(team_two_emoji) + str(team_two_name) + str(date)


        else:
            update.message.reply_text(match_text)
            match_text = "Тур " + str(game_tour)
            date = ""
            if game_date:
                date = ". " + str(game_date)
            if team_one_goals:
                match_text = match_text + "\n✅" + str(team_one_name) + str(team_one_emoji) + " " + str(team_one_goals) + " - " \
                             + str(team_two_goals) + " " + str(team_two_emoji) + str(team_two_name) + str(date)
            else:
                match_text = match_text + "\n⭕" + str(team_one_name) + str(team_one_emoji) + " - " + str(team_two_emoji) + str(team_two_name) + str(date)
            i += 1
    update.message.reply_text(match_text)
# end_add


# Added find all games and videos per opponent 02.04.2018
def opponent_menu(bot, update, chat_id, opponent_chat_id):
    keyboard_list = [
                    InlineKeyboardButton("❓Узнать, кто соперник 🤼‍♀", callback_data="opponent_info " + str(opponent_chat_id)),
                     InlineKeyboardButton("⚽Посмотреть результаты матчей соперника", callback_data="opponent_calendar " + str(opponent_chat_id)),
                     InlineKeyboardButton("🖥Посмотреть видео матчей соперника", callback_data="opponent_videos " + str(opponent_chat_id))
                     ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard_list, n_cols=1), resize_keyboard=True)
    time.sleep(1)
    bot.send_message(chat_id=chat_id, text='Чтобы подготовиться к игре, рекомендую:', reply_markup=reply_markup)

def team_calendar(bot, update, chat_id):
    team = getyourteam(chat_id, 2018)
    if team:
        update.message.reply_text("Результаты сыгранных матчей команды {}:".format(team))
        time.sleep(1)
        matches = getmatchschedule(team, '2018', '', 1)
        if len(matches) > 0:
            match_text = ""
            for match in matches:
                date = str(match[4]) + ": "
                match_text = match_text + "\n" + str(date) + str(match[0]) + str(match[6]) + " " + str(
                    match[2]) + " - " + str(match[3]) + " " + str(match[7]) + str(match[1])
        else:
            match_text = "Команда {} еще не сыграла ни одного матча 😳".format(team)
        update.message.reply_text(match_text)

def team_info(bot, update, team_id):
    """Send a message when the command /teamlist is issued."""
    TEAMS = getteaminfo(team_id)
    teamlist = ""
    i = 0
    for team in TEAMS:
        i = i + 1
        teamlist = teamlist + "\n" + team[2] + "\t" + team[3] + "\t" + team[1]
    update.message.reply_text(teamlist)

# end_add 02.04.2018
def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def showtable(bot, update):
    tables = gettournamenttable(6,None)
    #keyboard_list = []
    keyboard_list = [
                     InlineKeyboardButton("К", callback_data="ignore"),
                     InlineKeyboardButton("И", callback_data="ignore"),
                     InlineKeyboardButton("В", callback_data="ignore"),
                     InlineKeyboardButton("Н", callback_data="ignore"),
                     InlineKeyboardButton("П", callback_data="ignore"),
                     #InlineKeyboardButton("ГЗ", callback_data="ignore"),
                     #InlineKeyboardButton("ГП", callback_data="ignore"),
                     InlineKeyboardButton("Р", callback_data="ignore"),
                     InlineKeyboardButton("О", callback_data="ignore")
                     ]
    button_list = []
    for table in tables:
        i = 0
        #print(table)
        #keyboard.append(list(table))

        for col in table:
            if i > 0 and (i < 6 or i > 7):
                keyboard_list.append(InlineKeyboardButton(str(col), callback_data="ignore"))
            i = i + 1
    button_list = keyboard_list
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=7))

    update.message.reply_text('Турнирная таблица на текущий момент:', reply_markup=reply_markup)
    update.message.reply_text('К - команда, И - количество сыгранных матчей, В - победа, Н - ничья, П - поражение, ГЗ - голов забито, ГП - голов пропущено, Р - разница, О - очки')
    time.sleep(1)
    update.message.reply_text('Также можешь посмотреть в текстовом виде таблицу: /table')


def table(bot, update):
    chat_id = update.message.chat_id
    tables = gettournamenttable(6, None)
    teamsarr = []
    for r in tables:
        teamsarr.append(list(r))
    table_header = '|И_.|В_.|Н_.|П_.|ГЗ_|ГП_|Р_.|О_.|Команда'
    text = ""
    bot.send_message(chat_id=chat_id,
                     text='<b>' + table_header + '</b>',
                     parse_mode=ParseMode.HTML)
    #bot.send_message(chat_id=chat_id,
     #                text='<b>test<b>',
     #                parse_mode=ParseMode.HTML)
    row_format = "{} {} {} {} {} {} {} {} {}"
    #row_format = "{0:^20} {1:^5} {2:^5} {3:^5} {4:^5} {5:^5} {6:^5} {7:^5} {8:^5} {9:^5}"
    for oneteam in teamsarr:
        #team = str(oneteam[0]) + "_" * (11 - len(str(oneteam[0]))) if len(str(oneteam[0])) < 11 else str(oneteam[0])
        #team_emj = str(oneteam[1]) + "_" * (5 - len(str(oneteam[1]))) if len(str(oneteam[1])) < 5 else str(oneteam[1])
        team = oneteam[0]
        team_emj = " " + oneteam[1]
        games_count = str(oneteam[2]) + "_" * (3 - len(str(oneteam[2]))) if len(str(oneteam[2])) < 3 else str(oneteam[2])
        wins = str(oneteam[3]) + "_" * (3 - len(str(oneteam[3]))) if len(str(oneteam[3])) < 3 else str(oneteam[3])
        drows = str(oneteam[4]) + "_" * (3 - len(str(oneteam[4]))) if len(str(oneteam[4])) < 3 else str(oneteam[4])
        loses = str(oneteam[5]) + "_" * (3 - len(str(oneteam[5]))) if len(str(oneteam[5])) < 3 else str(oneteam[5])
        scored = str(oneteam[6]) + "_" * (3 - len(str(oneteam[6]))) if len(str(oneteam[6])) < 3 else str(oneteam[6])
        skipped = str(oneteam[7]) + "_" * (3 - len(str(oneteam[7]))) if len(str(oneteam[7])) < 3 else str(oneteam[7])
        diff = str(oneteam[8]) + "_" * (3 - len(str(oneteam[8]))) if len(str(oneteam[8])) < 3 else str(oneteam[8])
        points = str(oneteam[9]) + "_" * (3 - len(str(oneteam[9]))) if len(str(oneteam[9])) < 3 else str(oneteam[9])
        text = text + "\n" + "|" +  games_count + "|" +  wins + "|" +  drows + "|" +  loses + "|" +  scored + "|" +  skipped + "|" +  diff + "|" +  points + "|" +  team +  team_emj
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.HTML)

def ready2play(bot, update, state):
    chat_id = update.message.chat_id
    date = getnextsunday()
    cur_year = datetime.date.today().year
    ins2ready(chat_id, str(getnextsunday()), state)
    if not state:
        update.message.reply_text("🙁Очень жаль! Надеюсь, что в следующее воскресенье у тебя получится!")
        for chat_id in LIST_OF_ADMINS:
            bot.send_message(chat_id=chat_id,
                             text=update.message.from_user.first_name + " " + update.message.from_user.last_name + " сообщил, что не готов сыграть в ближайшее воскресенье " + str(
                                 getnextsunday()))
        team_id = getteamidbytchatid(chat_id, cur_year)
        game_id = getgameidbyteamid(team_id, date)
        if game_id:
            arr = ["date", game_id]
            set(bot, update, arr)
    else:
        update.message.reply_text("👏Спасибо, что сообщил! Буду иметь ввиду !👍")
        for chat_id in LIST_OF_ADMINS:
            bot.send_message(chat_id=chat_id,
                             text=update.message.from_user.first_name + " " + update.message.from_user.last_name + " сообщил о своей готовности сыграть в ближайшее воскресенье " + str(
                                 getnextsunday()))
    #gamecalendar(bot, update)


def autoready2play(bot, update, chat_id):
    is_ready = isready(chat_id, str(getnextsunday()), True)
    if is_ready > 0:
        pass
    else:
        ins2ready(chat_id, str(getnextsunday()), True)
        gamecalendar(bot, update)

def next5games(bot, update):
    chat_id = update.message.chat_id
    date = getnextsunday()
    cur_year = datetime.date.today().year
    matches = getmatchschedule('', cur_year, 5, 0)
    match_text = ""
    for match in matches:
        date = ""
        if match[4]:
            date = " (" + str(match[4]) + ")"
        match_text = match_text + "\n" + str(match[0]) + str(match[6]) + " - " + str(match[7]) + str(match[1]) + str(date)
    update.message.reply_text("Ближайшие 5️⃣ матчей по расписанию:")
    time.sleep(1)
    update.message.reply_text(match_text)
    time.sleep(2)

def showgamevideo(bot, update, opp_chat_id=None):
    print("we in showgamevideo")
    button_list = []
    cur_year = datetime.date.today().year
    date = getnextsunday()
    if not opp_chat_id:
        matches = getallplayedgames(cur_year)
    else:
        team = getyourteam(opp_chat_id, 2018)
        matches = getallplayedgames(cur_year, team)
    if len(matches) == 0:
        update.message.reply_text("Нет доступных видео")
    else:
        for match in matches:
            date_text = str(match[7]) + ": "
            match_text = str(date_text) + str(match[1]) + str(match[3]) + " - " + str(match[6]) + str(match[4]) + ". Тур " + str(match[8])
            #msg = re.sub('\s+', '_', match_text)
            #print(msg)
            data = "vid " + str(match[9]) + " " + str(match[3]) + "-" + str(match[6])
            #data = "vid " + str(match[9])
            #print(match_text + "data : " + data)
            button_list.append(InlineKeyboardButton(match_text, callback_data=data, resize_keyboard=True))
            #button_list.append(InlineKeyboardButton(set, callback_data=data, resize_keyboard=True))
        #print(button_list)
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1), resize_keyboard=True)
        time.sleep(1)
        update.message.reply_text('Выбери матч, который хочешь посмотреть', reply_markup=reply_markup)
        time.sleep(1)


def sendvideo(bot, update, file_id, caption):
    chat_id = update.message.chat_id
    #video = open('C:/Users/OlKudryavtsev/Documents/08_GitHub/voroshila/videos/137.mp4', 'rb')
    bot.sendVideo(chat_id=chat_id, video=file_id, caption=caption)


@restricted
def whoisready(bot, update, state):
    cur_year = datetime.date.today().year
    date = getnextsunday()
    if state == True:
        ready_teams = getwhoisready(cur_year, date, True)
        msg_text = ""
        for ready_team in ready_teams:
            msg_text = msg_text + "\n" + str(ready_team[3]) + "; " + str(ready_team[1]) + " " + str(ready_team[2])
        update.message.reply_text("На данный момент в ближайшее воскресенье " + str(date) + " готовы играть следующие команды:")
        time.sleep(1)
        update.message.reply_text(msg_text)

    elif state == False:
        not_ready_teams = getwhoisready(cur_year, date, False)
        msg_text = ""
        for not_ready_team in not_ready_teams:
            msg_text = msg_text + "\n" + str(not_ready_team[3]) + "; " + str(not_ready_team[1]) + " " + str(not_ready_team[2])
        update.message.reply_text("Не готовы играть следующие команды:")
        time.sleep(1)
        update.message.reply_text(msg_text)

@restricted
def possiblegames(bot, update):
    cur_year = datetime.date.today().year
    date = getnextsunday()
    matches = getpossiblegames(6, date, cur_year)
    if len(matches) == 0:
        update.message.reply_text("Из готовых участников невозможно составить пары 😔")
    else:
        match_text = ""
        for match in matches:
            if match[7]:
                date_text = "(" + str(match[7]) + ")"
            else:
                date_text = ""
            match_text = match_text + "\n" + str(match[0]) + ".\t" + str(match[1]) + " " + str(
            match[3]) + " - " + str(match[4]) + " " + str(match[6]) + ". Тур " + str(match[8]) + " " + str(date_text)
        update.message.reply_text("Из готовых участников доступны следующие пары:")
        time.sleep(1)
        update.message.reply_text(match_text)

@restricted
def msg(bot, update, args):
    """Send a message when the command /sendmessage is issued."""
    sender_chat_id = update.message.chat_id
    msg = ' '.join(args)
    #for arg in args:
    #    msg = msg + " " + arg
    chat_ids, firstnames, fullnames = getchatids()
    i = 0
    for chat_id, name in zip(chat_ids, firstnames):
        i = i + 1
        if not name:
            name = "уважаемый участник соревнования"
        bot.send_message(chat_id=chat_id, text=name + ", " + msg)
    msginsert(sender_chat_id, '', msg)

@restricted
def vsmsg(bot, update, args):
    """Send a message when the command /sendmessage is issued."""
    sender_chat_id = update.message.chat_id
    msg = ' '.join(args)
    #for arg in args:
    #    msg = msg + " " + arg
    chat_ids, firstnames, fullnames = getvschatids()
    i = 0
    for chat_id, name in zip(chat_ids, firstnames):
        i = i + 1
        if not name:
            name = "уважаемый участник соревнования"
        bot.send_message(chat_id=chat_id, text=name + ", " + msg)
    msginsert(sender_chat_id, '', msg)

@restricted
def admin(bot, update):
    """Send a message when the command /help is issued."""
    opponent_menu(bot, update, 230308082, 230308082)
    text = "Действия админисратора:"
    text += "\n/whoisready - получить игроков в статусе Готов"
    text += "\n/possiblegames - получить список пар, состоящих из игроков в статусе Готов"
    text += "\n/set - запланировать матч, выставить счет сыгранного матча"
    update.message.reply_text(text)

@restricted
def adminkey(bot, update):
    custom_keyboard = [["👻️Кто готов?", "🛌️Кто не готов?"],
                       ["🤼‍♀Готовые пары"],
                       ["Внести результат матча⚽"],
                       ["🔙Назад"]]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Что ты хочешь?', reply_markup=reply_markup)

@restricted
def showpossiblegames(bot, update):
    print("we in showpossiblegames")
    button_list = []
    cur_year = datetime.date.today().year
    date = getnextsunday()
    matches = getpossiblegames(6, date, cur_year)
    if len(matches) == 0:
        update.message.reply_text("Из готовых участников невозможно составить пары 😔")
    else:
        for match in matches:
            if match[7]:
                date_text = "(" + str(match[7]) + ")"
                set = "❌"
                data = "date " + str(match[0])
            else:
                date_text = ""
                set = "✅"
                data = "date " + str(match[0]) + " " + str(date)
            match_text = set + str(match[1]) + " " + str(match[3]) + " - " + str(match[4]) + " " + str(match[6]) + " [" + str(match[8]) + "] " + str(date_text)

            button_list.append(InlineKeyboardButton(match_text, callback_data=data, resize_keyboard=True))
            #button_list.append(InlineKeyboardButton(set, callback_data=data, resize_keyboard=True))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1), resize_keyboard=True)
        time.sleep(1)
        update.message.reply_text('Из готовых участников доступны следующие пары:', reply_markup=reply_markup)
        time.sleep(1)
        update.message.reply_text("Чтобы запланировать матч, нажми ✅\nЧтобы отменить матч, нажми ❌")

@restricted
def showplannedgames(bot, update):
    print("we in showplannedgames")
    button_list = []
    cur_year = datetime.date.today().year
    date = getnextsunday()
    matches = getplannedgames()
    if len(matches) == 0:
        update.message.reply_text("Нет запланированных матчей")
    else:
        for match in matches:
            date_text = "(" + str(match[7]) + ")"
            data = "scores " + str(match[0])
            match_text = str(match[1]) + " " + str(match[3]) + " - " + str(match[4]) + " " + str(match[6]) + " [" + str(match[8]) + "] " + str(date_text)

            button_list.append(InlineKeyboardButton(match_text, callback_data=data, resize_keyboard=True))
            #button_list.append(InlineKeyboardButton(set, callback_data=data, resize_keyboard=True))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1), resize_keyboard=True)
        time.sleep(1)
        update.message.reply_text('Для какого матча выставить счет?', reply_markup=reply_markup)
        time.sleep(1)

@restricted
def showscores(bot, update, game_id):
    keyboard_list = [
                     InlineKeyboardButton("0:0", callback_data="goal " + game_id + " 0 0"),
                     InlineKeyboardButton("0:1", callback_data="goal " + game_id + " 0 1"),
                     InlineKeyboardButton("0:2", callback_data="goal " + game_id + " 0 2"),
                     InlineKeyboardButton("0:3", callback_data="goal " + game_id + " 0 3"),
                     InlineKeyboardButton("1:0", callback_data="goal " + game_id + " 1 0"),
                     InlineKeyboardButton("1:1", callback_data="goal " + game_id + " 1 1"),
                     InlineKeyboardButton("1:2", callback_data="goal " + game_id + " 1 2"),
                     InlineKeyboardButton("1:3", callback_data="goal " + game_id + " 1 3"),
                     InlineKeyboardButton("2:0", callback_data="goal " + game_id + " 2 0"),
                     InlineKeyboardButton("2:1", callback_data="goal " + game_id + " 2 1"),
                     InlineKeyboardButton("2:2", callback_data="goal " + game_id + " 2 2"),
                     InlineKeyboardButton("2:3", callback_data="goal " + game_id + " 2 3"),
                     InlineKeyboardButton("3:0", callback_data="goal " + game_id + " 3 0"),
                     InlineKeyboardButton("3:1", callback_data="goal " + game_id + " 3 1"),
                     InlineKeyboardButton("3:2", callback_data="goal " + game_id + " 3 2"),
                     InlineKeyboardButton("3:3", callback_data="goal " + game_id + " 3 3")
                     ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard_list, n_cols=4), resize_keyboard=True)
    update.message.reply_text('Выбери счет:', reply_markup=reply_markup)


def button(bot, update):
    date = getnextsunday()
    query = update.callback_query
    qres = query.data.split()
    if query.data == "full_calendar":
        allgames(bot, query)

    elif qres[0] == "opponent_info":
        chat_id = qres[1]
        team_id = getteamidbytchatid(chat_id, 2018)
        team_info(bot, query, team_id)

    elif qres[0] == "opponent_calendar":
        chat_id = qres[1]
        team_calendar(bot, query, chat_id) #02.04.2018

    elif qres[0] == "opponent_videos":
        #opponent_videos(bot, query) #02.04.2018
        chat_id = qres[1]
        showgamevideo(bot, query, chat_id)

    elif qres[0] == "date":
        game_id = qres[1]
        set(bot, query, qres)
        #bot.edit_message_text(text="На ближайшее воскресенье запланирован матч (game_id = {})".format(game_id),
        #                  chat_id=query.message.chat_id,
        #                  message_id=query.message.message_id)
    elif qres[0] == "scores":
        game_id = qres[1]
        showscores(bot, query, game_id)

    elif qres[0] == "goal":
        game_id = qres[1]
        set(bot, query, qres)

    elif qres[0] == "vid":
        file_id = qres[1]
        caption = qres[2]
        sendvideo(bot, query, file_id, caption)

@restricted
def set(bot, update, args):
    if not args:
        cur_year = datetime.date.today().year
        matches = getnext5games(cur_year)
        match_text = ""
        for match in matches:
            match_text = match_text + "\n" + str(match[0]) + ".\t" + str(match[1]) + " (" + str(match[2]) + ") " + str(
                match[3]) + " - " + str(match[4]) + " (" + str(match[5]) + ") " + str(match[6])
        update.message.reply_text(match_text)
        time.sleep(1)
        update.message.reply_text(
            "Для установки даты проведения матча напиши\n'/set date game_id date(формат: YYYY-MM-DD)'\nДля установки результата матча напиши\n'/set goal game_id goals_one goals_two'")
    elif args[0] == 'date':
        if len(args) == 3:
            chat_id = ""
            insdate(args[1], args[2])
            team_ids = getteamsidingame(args[1])
            chat_ids = []
            for team_id in team_ids:
                chat_id = getchatidbyteamid(team_id)
                chat_ids.append(chat_id)
            for team_id, chat_id in zip(team_ids, chat_ids):
                #chat_id = getchatidbyteamid(team_id)
                arr = ["ready", chat_id]
                set(bot, update, arr)
                first_name = getfullnamebychatid(chat_id)
                msg_text = first_name + ", матч с твоим участием запланирован на ближайшее воскресенье " + str(
                    getnextsunday())
                bot.send_message(chat_id=chat_id, text=msg_text)
                time.sleep(1)
                msg_text = "Если ты не готов играть, сообщи об этом, нажав кнопку '🚷Отменить готовность' в меню '🔜Ближайшие матчи' или нажав на /cancel"
                bot.send_message(chat_id=chat_id, text=msg_text)
                for tmp_chat_id in chat_ids:
                    if chat_id != tmp_chat_id:
                        opponent_chat_id = tmp_chat_id
                        opponent_menu(bot, update, chat_id, opponent_chat_id)
            update.message.reply_text("Дата успешно выставлена")
        elif len(args) == 2:
            chat_id = ""
            insdate(args[1], '')
            team_ids = getteamsidingame(args[1])
            for team_id in team_ids:
                chat_id = getchatidbyteamid(team_id)
                first_name = getfullnamebychatid(chat_id)
                time.sleep(1)
                msg_text = first_name + ", матч с твоим участием отменен"
                bot.send_message(chat_id=chat_id, text=msg_text)
            update.message.reply_text("Дата успешно удалена")
    elif args[0] == 'goal':
        if len(args) == 4:
            insgoal(args[1], args[2], args[3])
        elif len(args) < 4:
            insgoal(args[1], '', '')
        update.message.reply_text("Результат матча успешно установлен")
    elif args[0] == 'ready':
        autoready2play(bot, update, args[1])

    else:
        update.message.reply_text(
            "Для установки даты проведения матча напиши '/set date game_id date(YYYY-MM-DD'\nДля установки результата матча напиши '/set goal game_id goals_one goals_two'")

@restricted
def setvideo(bot, update, args):
    game_id = args[0]
    video_id = args[1]
    insvideoid(game_id, video_id)
    update.message.reply_text("Идентификатор видео-файла успешно выставлен")