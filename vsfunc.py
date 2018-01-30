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

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging
from functools import wraps
from emoji import emojize
import time
import datetime

import os, fnmatch
import re

import postgresql


def getfantasyid(line):
    key, sep, value = line.strip().partition(";")
    return value

def dbconnect():
    db = postgresql.open('pq://zabbix:zabbix@tbsm.croc.ru:5432/voroshila')
    return db

def insertnewuser(chat_id, first_name, last_name):
    db = dbconnect()
    check = db.query("SELECT * FROM public.reg_users where chat_id = '" + str(chat_id) + "'");
    if check:
        print("this user already exists in table")
    else:
        db.query("INSERT INTO voroshila.public.reg_users (chat_id, first_name, last_name) VALUES  	('" + str(chat_id) + "', '" + str(first_name) + "', '" + str(last_name)+ "')")

def getchatids():
    chat_ids = []
    firstnames = []
    fullnames = []
    db = dbconnect()
    results = db.query("SELECT * FROM public.reg_users");
    user_list = ""
    for result in results:
        chat_ids.append(str(result[1]))
        firstnames.append(str(result[2]))
        fullnames.append(str(result[4]))
    return chat_ids,firstnames,fullnames

def getvschatids():
    chat_ids = []
    firstnames = []
    fullnames = []
    db = dbconnect()
    results = db.query("SELECT * FROM public.reg_users where vs18 = true");
    user_list = ""
    for result in results:
        chat_ids.append(str(result[1]))
        firstnames.append(str(result[2]))
        fullnames.append(str(result[4]))
    return chat_ids,firstnames,fullnames

def getteaminfo():
    db = dbconnect()
    teams = db.query("SELECT * FROM public.teams where year=2018 order by team_name")
    return teams

def gettournamenttable(tid):
    db = dbconnect()
    select = """
select tm.team_name,tm.team_emoji,
  sum(win) + sum(loss) + sum(draw)as game,
  sum(win) as win, 
  sum(loss) as loss, 
  sum(draw) as draw, 
  sum(goals_s) as goals_s, 
  sum(goals_m) as goals_m,
  sum(goals_s) - sum(goals_m) as goals_d,
  sum(win)*3 + sum(draw) as points 
from (
select g.id_team_one as id_team, 
  CASE WHEN g.goals_one>g.goals_two THEN 1 ELSE 0 END as win,
  CASE WHEN g.goals_one<g.goals_two THEN 1 ELSE 0 END as loss,
  CASE WHEN g.goals_one=g.goals_two THEN 1 ELSE 0 END as draw,
  CASE WHEN g.goals_one IS NOT NULL THEN goals_one ELSE 0 END as goals_s,
  CASE WHEN g.goals_two IS NOT NULL THEN goals_two ELSE 0 END as goals_m
from games g where id_tournament="""+str(tid)+"""
union all
select g.id_team_two as id_team, 
  CASE WHEN g.goals_one<g.goals_two THEN 1 ELSE 0 END as win,
  CASE WHEN g.goals_one>g.goals_two THEN 1 ELSE 0 END as loss,
  CASE WHEN g.goals_one=g.goals_two THEN 1 ELSE 0 END as draw,
  CASE WHEN g.goals_two IS NOT NULL THEN goals_two ELSE 0 END as goals_s,
  CASE WHEN g.goals_one IS NOT NULL THEN goals_one ELSE 0 END as goals_m
from games g where id_tournament="""+str(tid)+"""
) t, teams tm where tm.team_id=t.id_team group by tm.team_name,tm.team_emoji order by points desc, goals_d desc
    """
    table = db.query(select)
    return table


def getteamlist(year):
    db = dbconnect()
    team_list = []
    select = "select team_name from teams where year='" + str(year) + "' order by team_name"
    teamlists = db.query(select)
    for teamlist in teamlists:
        team_list.append(teamlist[0])
    return team_list



def getmatchschedule(team_name, year, top, is_played):
    db = dbconnect()
    select = ""
    #все матчи определенной команды
    if team_name != '' and top == '' and is_played == 1:
        select = """
select t1.team_name, t2.team_name, g.goals_one, g.goals_two, g.date, g.tour, t1.team_emoji, t2.team_emoji from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ and (t1.team_name = '"""+ team_name + """' or t2.team_name = '""" + team_name + """') and g.goals_one > -1 order by g.tour, g.id_game
"""
    if team_name != '' and top == '' and is_played == 0:
        select = """
select t1.team_name, t2.team_name, g.goals_one, g.goals_two, g.date, g.tour, t1.team_emoji, t2.team_emoji from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ and (t1.team_name = '""" + team_name + """' or t2.team_name = '""" + team_name + """') and g.goals_one is NULL order by g.tour, g.id_game
"""

    elif team_name == '' and top != '' and is_played == 1:
        select = """
select t1.team_name, t2.team_name, g.goals_one, g.goals_two, g.date, g.tour, t1.team_emoji, t2.team_emoji from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ and g.goals_one > -1 order by g.tour, g.id_game fetch first """ + str(top) + """ rows only
"""

    elif team_name == '' and top != '' and is_played == 0:
        select = """
select t1.team_name, t2.team_name, g.goals_one, g.goals_two, g.date, g.tour, t1.team_emoji, t2.team_emoji from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ and g.goals_one is NULL order by g.tour, g.id_game fetch first """ + str(top) + """ rows only
"""

    matches = db.query(select)
    return matches

def getyourteam(chat_id, year):
    db = dbconnect()
    select = "select t.team_name from reg_users u, teams t where u.full_name = t.full_name and year = " + str(year) + "and u.chat_id = '"+ str(chat_id) + "'"
    yourteam = db.query(select)
    print(yourteam[0][0])
    return yourteam[0][0]

def msginsert(sender_chat_id, receiver_chat_id, msg):
    db = dbconnect()
    insert = """
INSERT INTO voroshila.public.messages (msg_from, msg_to, datetime, message)
VALUES ('""" + str(sender_chat_id) + """', '""" + str(receiver_chat_id) + """',CURRENT_TIMESTAMP , '""" + str(msg) + """')
"""
    db.query(insert)

def queryinsert(sender_chat_id, query):
    db = dbconnect()
    insert = """
INSERT INTO voroshila.public.queries (chat_id, query, datetime)
VALUES ('""" + str(sender_chat_id) + """', '""" + str(query) + """', CURRENT_TIMESTAMP)
"""
    db.query(insert)


def getnextsunday():
    today = datetime.date.today()
    sunday = today + datetime.timedelta((6 - today.weekday()) % 7)
    return sunday

def isready(chat_id, date, state):
    db = dbconnect()
    select = "select count(rdy_id) from voroshila.public.ready2play where chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "' and is_ready = " + str(state)
    res = db.query(select)
    return res[0][0]

def answaboutready(chat_id, date):
    db = dbconnect()
    select = "select count(rdy_id) from voroshila.public.ready2play where chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "'"
    res = db.query(select)
    return res[0][0]

def ins2ready(chat_id, date, state):
    db = dbconnect()
    isanswer = answaboutready(chat_id, date)
    if isanswer > 0:
        insert = "UPDATE voroshila.public.ready2play set is_ready=" + str(state) + " WHERE chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "'"
    else:
        insert = "INSERT INTO voroshila.public.ready2play (chat_id, date, is_ready) VALUES ('" + str(chat_id) + "', '" + str(date) + "', " + str(state) + ")"
    db.query(insert)

def delfromready(chat_id, date):
    db = dbconnect()
    delete = "DELETE FROM voroshila.public.ready2play where chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "'"
    db.query(delete)

def getnext5games(year):
    db = dbconnect()
    select = """
select  g.id_game, t1.team_name, g.id_team_one, t1.team_emoji, t2.team_name, g.id_team_two, t2.team_emoji, g.date, g.tour from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ and g.goals_one is NULL order by g.tour, g.id_game fetch first 5 rows only
"""
    matches = db.query(select)
    return matches


def getpossiblegames(id_tournament, date, year):
    db = dbconnect()
    select = """
select g.id_game, t1.team_name, g.id_team_one, t1.team_emoji, t2.team_name, g.id_team_two, t2.team_emoji, g.date, g.tour from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where g.id_tournament = """ + str(id_tournament) + """  and g.goals_one IS NULL and g.id_team_one in 
(select team_id from teams t, ready2play r, reg_users u where t.full_name = u.full_name and u.chat_id = r.chat_id and r.is_ready = TRUE and year = """ + str(year) + """ and r.date = '""" + str(date) + """') 
and g.id_team_two in
(select team_id from teams t, ready2play r, reg_users u where t.full_name = u.full_name and u.chat_id = r.chat_id and r.is_ready = TRUE and year = """ + str(year) + """ and r.date = '""" + str(date) + """')      
order by g.tour, g.id_game
fetch first 5 rows only
"""
    matches = db.query(select)
    return matches


def getplannedgames(date):
    db = dbconnect()
    select = """
select g.id_game, t1.team_name, g.id_team_one, t1.team_emoji, t2.team_name, g.id_team_two, t2.team_emoji, g.date, g.tour from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where g.date = '""" + str(date) + """'      
order by g.id_game
"""
    matches = db.query(select)
    return matches

def insdate(game_id, date):
    db = dbconnect()
    if date != '':
        update = "UPDATE voroshila.public.games SET date = '" + str(date) + "' WHERE id_game = " + str(game_id)
    else:
        update = "UPDATE voroshila.public.games SET date = NULL WHERE id_game = " + str(game_id)
    db.query(update)

def insgoal(game_id, goals_one, goals_two):
    db = dbconnect()
    if goals_one != '':
        update = "UPDATE voroshila.public.games SET goals_one = " + str(goals_one) + ",	goals_two = " + str(goals_two) + " WHERE id_game = " + str(game_id)
    else:
        update = "UPDATE voroshila.public.games SET goals_one = NULL,	goals_two = NULL WHERE id_game = " + str(game_id)
    db.query(update)

def getteamsidingame(game_id):
    db = dbconnect()
    select = "select id_team_one, id_team_two from games where id_game = " + str(game_id)
    team_ids = db.query(select)
    return team_ids[0]

def getchatidbyteamid(team_id):
    db = dbconnect()
    select = "select u.chat_id from teams t, reg_users u where t.full_name = u.full_name and t.team_id = " + str(team_id)
    chat_ids = db.query(select)
    return chat_ids[0][0]

def getteamidbytchatid(chat_id, year):
    db = dbconnect()
    select = "select t.team_id from teams t, reg_users u where t.full_name = u.full_name and u.chat_id = '" + str(chat_id) +"' and t.year = " + str(year)
    team_ids = db.query(select)
    return team_ids[0][0]

def getgameidbyteamid(team_id):
    db = dbconnect()
    select = "select distinct (g.id_game) from games g, reg_users u, ready2play r where  g.date IS NOT NULL and g.date = r.date and (g.id_team_one = " + str(team_id) + " or g.id_team_two = " + str(team_id) + ")"
    game_ids = db.query(select)
    return game_ids[0][0]

def getfullnamebychatid(chat_id):
    db = dbconnect()
    select = "select full_name from reg_users where chat_id = '" + str(chat_id) + "'"
    first_names = db.query(select)
    return first_names[0][0]

def getwhoisready(year, date, state):
    db = dbconnect()
    select = "select distinct t.team_id, t.team_name, t.team_emoji, u.full_name from teams t,  reg_users u, ready2play r where t.full_name = u.full_name and t.year = " + str(year) + " and r.date = '"+ str(date) + "' and u.chat_id in (select chat_id from ready2play where is_ready = " + str(state) + " and date = '" + str(date) + "') order by t.team_id"
    ready_teams = db.query(select)
    return ready_teams

def print_table(table):
    col_width = [max(len(x) for x in col) for col in zip(*table)]
    for line in table:
        print("| " + " | ".join("{:{}}".format(x, col_width[i])
                                for i, x in enumerate(line)) + " |")
