#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler,ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging
from functools import wraps
from emoji import emojize
import time

import os, fnmatch
import re

from vshandlers import *

#TOKEN = "504482288:AAH3OmmyUQ_LyxNZWj2D4nU356PxHtIX_68"
TOKEN = "542202315:AAFABS2cZAkBSx4WpqNs5P7USsJv_0ZYA4E"
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))



    dp.add_handler(CommandHandler('keyboard', keyboard))
    dp.add_handler(CommandHandler('yearchoise', yearchoise))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("teamlist", teamlist))
    dp.add_handler(CommandHandler("reglament", reglament))
    dp.add_handler(CommandHandler("winners", winners))
    dp.add_handler(CommandHandler("links", links))
    dp.add_handler(CommandHandler("table2017", table2017))
    dp.add_handler(CommandHandler("msg", msg, pass_args=True))
    dp.add_handler(CommandHandler("vsmsg", vsmsg, pass_args=True))
    dp.add_handler(CommandHandler("msgto", msgto, pass_args=True))
    dp.add_handler(CommandHandler("mywish", mywish, pass_args=True))
    dp.add_handler(CommandHandler('teams', teams))

    dp.add_handler(CommandHandler('shuffle', shuffle))
    # on noncommand i.e message - echo the message on Telegram

    dp.add_handler(CommandHandler('gamecalendar', gamecalendar))
    dp.add_handler(CommandHandler('gameresult', gameresult))
    dp.add_handler(CommandHandler('ready2play', ready2play))
    dp.add_handler(CommandHandler('cancel', ready2play))

    #admin handlers
    dp.add_handler(CommandHandler('admin', admin))
    dp.add_handler(CommandHandler('whoisready', whoisready))
    dp.add_handler(CommandHandler('possiblegames', possiblegames))
    dp.add_handler(CommandHandler("set", set, pass_args=True))

    dp.add_handler(MessageHandler(Filters.text, keyboardecho))
    dp.add_handler(MessageHandler(Filters.text, echo))
    #dp.add_handler(MessageHandler(Filters.text, matchschedule))



    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()