#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging
from functools import wraps
from emoji import emojize
import time
import datetime
import random
from tabulate import tabulate

import os, fnmatch
import re

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
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
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
    insertnewuser(chat_id, update.message.from_user.first_name, update.message.from_user.last_name)
    bot.send_message(chat_id=230308082,
                     text="Зарегистрирован новый пользователь: " + update.message.from_user.first_name + " " + update.message.from_user.last_name)
    update.message.reply_text('Привет, {}!'.format(update.message.from_user.first_name))
    update.message.reply_text('Тебя приветствует официальный бот турнира Ворошиловский стрелок ⚽️👍!')
    keyboard(bot, update)
    # update.message.reply_text('Чтобы посмотреть, что я умею, напиши /help')


def help(bot, update):
    """Send a message when the command /help is issued."""
    text = "Смотри, что я умею:"
    text += "\n/teamlist - получить список зарегистрировшихся участников"
    text += "\n/reglament - показать регламент турнира ВС2018"
    text += "\n/winners - показать список победителей прошлых турниров"
    text += "\n/links - показать ссылки на GoogleDocs"
    text += "\n/table2017 - показать турнирную таблицу ВС2017"
    text += "\n/msgto - написать сообщение определенному контакту"
    text += "\n\nА еще ты можешь мне просто писать 'победители','помощь','покажи таблицу' и т.д."
    update.message.reply_text(text)


# функция, показывающая список зарегистрировавшихся команд
def teamlist(bot, update):
    """Send a message when the command /teamlist is issued."""
    TEAMS = getteaminfo()
    teamlist = ""
    i = 0
    for team in TEAMS:
        i = i + 1
        teamlist = teamlist + "\n" + str(i) + ". " + "\t" + team[2] + "\t" + team[3] + "\t" + team[1]
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
Система: сезон, 10 команд, 1 круг.
По итогам групп состоятся 2 розыгрыша плейофф - основная сетка и сетка "лузеров".
1 и 2 место "регулярки" сразу выходят в полуфинал.
3-6 места образуют две пары 1/4 плейофф (3-6, 4-5).
7-10 места образуют два полуфинала сетки "лузеров" (7-10, 8-9).

Суммарное количество игр в сезоне - 54 (45 регулярка, 6 основной плейофф, 3 - "лузеров").

Призы "регулярки":
1 место - 1000р
2-3 места - по 500р
4-6 места - по 250р

Призы "чемпионата":
🥇 - 3000р
🥈 - 2000р
🥉 - 1000р
🏆 сетки "лузеров" - 1000р

Старт турнира: 28.01.2018.
Календарь игр будет опубликован в течение недели.
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
        update.message.reply_text('К сожалению, я тебя не понял 😔')
        help(bot, update)


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

    custom_keyboard = [["🔛Результаты матчей", "🔜Ближайшие матчи"],
                       ["⚽Список участников", "📝Регламент турнира"],
                       ["📅Архив"],
                       ["✏Отправить сообщение"],
                       ["⚠Помощь"]]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Можешь выбрать:', reply_markup=reply_markup)


# функция выбора года (надо заменить на беседу)
def yearchoise(bot, update):
    keyboard = [[InlineKeyboardButton("2️⃣0️⃣1️⃣7️⃣", callback_data='2017'),
                 InlineKeyboardButton("2️⃣0️⃣1️⃣8️⃣", callback_data='2018')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Выбери год:', reply_markup=reply_markup)


@restricted
def msg(bot, update, args):
    """Send a message when the command /sendmessage is issued."""
    sender_chat_id = update.message.chat_id
    msg = ' '.join(args)
    for arg in args:
        msg = msg + " " + arg
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
    echotext = update.message.text
    queryinsert(sender_chat_id, echotext)
    # echotext = echotext.lower()
    if echotext == "⚽Список участников":
        teamlist(bot, update)

    elif echotext == "📝Регламент турнира":
        reglament(bot, update)

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
        gamecalendar(bot, update)

    elif echotext == "🔜Ближайшие матчи":
        chat_id = update.message.chat_id
        date = getnextsunday()
        matches = getplannedgames(date)
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
            time.sleep(2)
        gamecalendar(bot, update)


    elif echotext == "🔛Результаты матчей":
        chat_id = update.message.chat_id
        matches = getmatchschedule('', '2018', 5, 1)
        match_text = ""
        for match in matches:
            date = ""
            if match[4]:
                date = " (" + str(match[4]) + ")"
            match_text = match_text + "\n" + str(match[0]) + str(match[6]) + " " + str(match[2]) + " - " + str(
                match[3]) + " " + str(match[7]) + str(match[1]) + str(date)
        update.message.reply_text("Последние 5️⃣  сыгранных матчей:")
        time.sleep(1)
        update.message.reply_text(match_text)
        time.sleep(2)
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
        update.message.reply_text("Ты еще не сыграл ни одной игры 😳")
        gamecalendar(bot, update)

    elif echotext == "🗓Турнирная таблица":
        chat_id = str(update.message.chat_id)
        tables = gettournamenttable(6)
        tabletxt = ""
        row = ""
        for r in tables:
            row = row + "\n"
            for f in r:
                row = row + "\t     " + str(f)
        tabletxt = tabletxt + "\n" + row
        update.message.reply_text("Команда\t\tВ\t\tН\t\tП\t\tЗабито\t\tПропущено\t\tРазница\t\tОчки" + tabletxt)
        #update.message.reply_text(tabletxt)
        gameresult(bot, update)

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

def gameresult(bot, update):
    print("we in gameresult")
    chat_id = update.message.chat_id
    reply_keyboard = [["🗓Турнирная таблица"],
                          ["⭕Свои оставшиеся матчи", "✅Свои сыгранные матчи"],
                          ["🔙Назад"]]
    text = "Также можешь посмотреть 👇🏽"

    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def ready2play(bot, update, state):
    chat_id = update.message.chat_id
    cur_year = datetime.date.today().year
    ins2ready(chat_id, str(getnextsunday()), state)
    if not state:
        update.message.reply_text("🙁Очень жаль! Надеюсь, что в следующее воскресенье у тебя получится!")
        for chat_id in LIST_OF_ADMINS:
            bot.send_message(chat_id=chat_id,
                             text=update.message.from_user.first_name + " " + update.message.from_user.last_name + " сообщил об отмене своей готовности сыграть в ближайшее воскресенье " + str(
                                 getnextsunday()))
        team_id = getteamidbytchatid(chat_id, cur_year)
        game_id = getgameidbyteamid(team_id)
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


@restricted
def set(bot, update, args):
    if  not args:
        cur_year = datetime.date.today().year
        matches = getnext5games(cur_year)
        match_text = ""
        for match in matches:
            match_text = match_text + "\n" + str(match[0]) + ".\t" + str(match[1]) + " (" + str(match[2]) + ") " + str(
                match[3]) + " - " + str(match[4]) + " (" + str(match[5]) + ") " + str(match[6])
        update.message.reply_text(match_text)
        update.message.reply_text(
            "Для установки даты проведения матча напиши '/set date game_id date(формат: YYYY-MM-DD)'\nДля установки результата матча напиши '/set goal game_id goals_one goals_two'")
    elif args[0] == 'date':
        if len(args) == 3:
            chat_id = ""
            insdate(args[1], args[2])
            team_ids = getteamsidingame(args[1])
            for team_id in team_ids:
                chat_id = getchatidbyteamid(team_id)
                arr = ["ready", chat_id]
                set(bot, update, arr)
                first_name = getfullnamebychatid(chat_id)
                msg_text = first_name + ", матч с твоим участием запланирован на ближайшее воскресенье " + str(
                    getnextsunday())
                bot.send_message(chat_id=chat_id, text=msg_text)
                time.sleep(1)
                msg_text = "Если ты не готов играть, сообщи об этом, нажав кнопку '🚷Отменить готовность' в меню '🔜Ближайшие матчи' или нажав на /cancel"
                bot.send_message(chat_id=chat_id, text=msg_text)
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
def whoisready(bot, update):
    cur_year = datetime.date.today().year
    date = getnextsunday()
    ready_teams = getwhoisready(cur_year, date)
    msg_text = ""
    for ready_team in ready_teams:
        msg_text = msg_text + "\n" + str(ready_team[0]) + ". " + str(ready_team[3]) + "    " + str(ready_team[1]) + " " + str(ready_team[2])
    update.message.reply_text("На данный момент в ближайшее воскресенье " + str(date) + " готовы играть следующие команды:")
    time.sleep(1)
    update.message.reply_text(msg_text)
    time.sleep(1)
    possiblegames(bot, update)

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
def admin(bot, update):
    """Send a message when the command /help is issued."""
    text = "Действия админисратора:"
    text += "\n/whoisready - получить игроков в статусе Готов"
    text += "\n/possiblegames - получить список пар, состоящих из игроков в статусе Готов"
    text += "\n/set - запланировать матч, выставить счет сыгранного матча"
    update.message.reply_text(text)

