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

import fnmatch
import re

import postgresql
import psycopg2
import os
import urllib.parse as urlparse

def getfantasyid(line):
    key, sep, value = line.strip().partition(";")
    return value

def dbconnect():
    DATABASE_URL = os.environ['DATABASE_URL']
    #DATABASE_URL = "postgres://vqlxttzxuofmmb:9cc0458d1dc1c7bfb6ca2fa0d0cfa2d3c43822838d173501285bc429e43fa1a4@ec2-54-217-214-201.eu-west-1.compute.amazonaws.com:5432/d1t887nls7ecck"
    url = urlparse.urlparse(DATABASE_URL)
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    return conn, cursor
##    db = postgresql.open('pq://zabbix:zabbix@tbsm.croc.ru:5432/voroshila')
##    return db

def insertnewuser(chat_id, first_name, last_name):
    conn, cursor = dbconnect()
    cursor.execute("SELECT * FROM public.reg_users where chat_id = '" + str(chat_id) + "'")
    check = cursor.fetchall()
    ##db = dbconnect()
    ##check = db.query("SELECT * FROM public.reg_users where chat_id = '" + str(chat_id) + "'")
    if check:
        print("this user already exists in table")
    else:
        cursor.execute("INSERT INTO .reg_users (chat_id, first_name, last_name) VALUES  	('" + str(chat_id) + "', '" + str(first_name) + "', '" + str(last_name)+ "')")
    ##    db.query("INSERT INTO .reg_users (chat_id, first_name, last_name) VALUES  	('" + str(chat_id) + "', '" + str(first_name) + "', '" + str(last_name)+ "')")
    conn.commit()
    cursor.close()

def getchatids():
    chat_ids = []
    firstnames = []
    fullnames = []
    conn, cursor = dbconnect()
    cursor.execute("SELECT * FROM public.reg_users")
    results = cursor.fetchall()
    ##db = dbconnect()
    ##results = db.query("SELECT * FROM public.reg_users");
    for result in results:
        chat_ids.append(str(result[1]))
        firstnames.append(str(result[2]))
        fullnames.append(str(result[4]))
    conn.commit()
    cursor.close()
    return chat_ids,firstnames,fullnames

def getvschatids():
    chat_ids = []
    firstnames = []
    fullnames = []
    conn, cursor = dbconnect()
    cursor.execute("SELECT * FROM public.reg_users where vs18 = true")
    results = cursor.fetchall()
    ##db = dbconnect()
    ##results = db.query("SELECT * FROM public.reg_users where vs18 = true");
    for result in results:
        chat_ids.append(str(result[1]))
        firstnames.append(str(result[2]))
        fullnames.append(str(result[4]))
    conn.commit()
    cursor.close()
    return chat_ids,firstnames,fullnames

def getteaminfo(team_id = None):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    if team_id:
        cursor.execute("SELECT * FROM public.teams where team_id = " + str(team_id))
        teams = cursor.fetchall()
        ##teams = db.query("SELECT * FROM public.teams where team_id = " + str(team_id))
    else:
        cursor.execute("SELECT * FROM public.teams where year=2018 order by team_name")
        teams = cursor.fetchall()
        ##teams = db.query("SELECT * FROM public.teams where year=2018 order by team_name")
    conn.commit()
    cursor.close()
    return teams

def gettournamenttable(tid, col):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    if not col:
        order = "order by points desc, goals_d desc"
    else:
        order = "order by " + col + " desc"
    select = """
select tm.team_name,tm.team_emoji,
  sum(win) + sum(loss) + sum(draw)as game,
  sum(win) as win, 
  sum(draw) as draw,
  sum(loss) as loss, 
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
) t, teams tm where tm.team_id=t.id_team group by tm.team_name,tm.team_emoji """ + order
    cursor.execute(select)
    table = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##table = db.query(select)
    return table


def getteamlist(year):
    conn, cursor = dbconnect()

##    db = dbconnect()
    team_list = []
    select = "select team_name from teams where year='" + str(year) + "' order by team_name"
    cursor.execute(select)
    teamlists = cursor.fetchall()
##    teamlists = db.query(select)
    for teamlist in teamlists:
        team_list.append(teamlist[0])
    conn.commit()
    cursor.close()
    return team_list


def getmatchschedule(team_name, year, top, is_played):
    conn, cursor = dbconnect()
    ##db = dbconnect()
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
where t1.year = """ + str(year) + """ and g.goals_one > -1 order by g.date desc, g.tour desc fetch first """ + str(top) + """ rows only
"""

    elif team_name == '' and top != '' and is_played == 0:
        select = """
select t1.team_name, t2.team_name, g.goals_one, g.goals_two, g.date, g.tour, t1.team_emoji, t2.team_emoji from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ and g.goals_one is NULL order by g.tour, g.id_game fetch first """ + str(top) + """ rows only
"""
    elif not team_name and not top and not is_played:
        select = """
select t1.team_name, t2.team_name, g.goals_one, g.goals_two, g.date, g.tour, t1.team_emoji, t2.team_emoji from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ order by g.tour, g.id_game
"""
    cursor.execute(select)
    matches = cursor.fetchall()
    ##matches = db.query(select)
    conn.commit()
    cursor.close()
    return matches

def getyourteam(chat_id, year):
    conn, cursor = dbconnect()
    select = "select t.team_name from reg_users u, teams t where u.full_name = t.full_name and year = " + str(year) + "and u.chat_id = '"+ str(chat_id) + "'"
    cursor.execute(select)
    yourteam = cursor.fetchall()
    ##yourteam = db.query(select)
    print(yourteam[0][0])
    conn.commit()
    cursor.close()
    return yourteam[0][0]

def msginsert(sender_chat_id, receiver_chat_id, msg):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    insert = """
INSERT INTO .messages (msg_from, msg_to, datetime, message)
VALUES ('""" + str(sender_chat_id) + """', '""" + str(receiver_chat_id) + """',CURRENT_TIMESTAMP , '""" + str(msg) + """')
"""
    cursor.execute(insert)
    conn.commit()
    cursor.close()
    ##db.query(insert)

def queryinsert(sender_chat_id, query):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    insert = """
INSERT INTO queries (chat_id, query, datetime)
VALUES ('""" + str(sender_chat_id) + """', '""" + str(query) + """', CURRENT_TIMESTAMP)
"""
    cursor.execute(insert)
    conn.commit()
    cursor.close()
    ##db.query(insert)


def getnextsunday():
    today = datetime.date.today()
    sunday = today + datetime.timedelta((6 - today.weekday()) % 7)
    return sunday

def isready(chat_id, date, state):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select count(rdy_id) from ready2play where chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "' and is_ready = " + str(state)
    cursor.execute(select)
    res = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##res = db.query(select)
    return res[0][0]

def answaboutready(chat_id, date):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select count(rdy_id) from ready2play where chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "'"
    cursor.execute(select)
    res = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##res = db.query(select)
    return res[0][0]

def ins2ready(chat_id, date, state):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    isanswer = answaboutready(chat_id, date)
    if isanswer > 0:
        insert = "UPDATE .ready2play set is_ready=" + str(state) + " WHERE chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "'"
    else:
        insert = "INSERT INTO .ready2play (chat_id, date, is_ready) VALUES ('" + str(chat_id) + "', '" + str(date) + "', " + str(state) + ")"
    cursor.execute(insert)
    conn.commit()
    cursor.close()
    ##db.query(insert)

def delfromready(chat_id, date):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    delete = "DELETE FROM .ready2play where chat_id = '" + str(chat_id) + "' and date = '" + str(date) + "'"
    cursor.execute(delete)
    conn.commit()
    cursor.close()
    ##db.query(delete)

def getnext5games(year):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = """
select  g.id_game, t1.team_name, g.id_team_one, t1.team_emoji, t2.team_name, g.id_team_two, t2.team_emoji, g.date, g.tour from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where t1.year = """ + str(year) + """ and g.goals_one is NULL order by g.tour, g.id_game fetch first 5 rows only
"""
    cursor.execute(select)
    matches = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##matches = db.query(select)
    return matches


def getpossiblegames(id_tournament, date, year):
    conn, cursor = dbconnect()
    ##db = dbconnect()
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
    cursor.execute(select)
    matches = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##matches = db.query(select)
    return matches


def getplannedgames():
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = """
select g.id_game, t1.team_name, g.id_team_one, t1.team_emoji, t2.team_name, g.id_team_two, t2.team_emoji, g.date, g.tour from games g
inner join teams t1 ON g.id_team_one=t1.team_id
inner join teams t2 ON g.id_team_two=t2.team_id
where g.date IS NOT NULL and  g.goals_one IS NULL 
order by g.id_game
"""
    cursor.execute(select)
    matches = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##matches = db.query(select)
    return matches

def insdate(game_id, date):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    if date != '':
        update = "UPDATE .games SET date = '" + str(date) + "' WHERE id_game = " + str(game_id)
    else:
        update = "UPDATE .games SET date = NULL WHERE id_game = " + str(game_id)
    cursor.execute(update)
    conn.commit()
    cursor.close()
    ##db.query(update)

def insgoal(game_id, goals_one, goals_two):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    if goals_one != '':
        update = "UPDATE .games SET goals_one = " + str(goals_one) + ",	goals_two = " + str(goals_two) + " WHERE id_game = " + str(game_id)
    else:
        update = "UPDATE .games SET goals_one = NULL,	goals_two = NULL WHERE id_game = " + str(game_id)
    cursor.execute(update)
    conn.commit()
    cursor.close()
    ##db.query(update)

def getteamsidingame(game_id):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select id_team_one, id_team_two from games where id_game = " + str(game_id)
    cursor.execute(select)
    team_ids = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##team_ids = db.query(select)
    return team_ids[0]

def getchatidbyteamid(team_id):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select u.chat_id from teams t, reg_users u where t.full_name = u.full_name and t.team_id = " + str(team_id)
    cursor.execute(select)
    chat_ids = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##chat_ids = db.query(select)
    return chat_ids[0][0]

def getteamidbytchatid(chat_id, year):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select t.team_id from teams t, reg_users u where t.full_name = u.full_name and u.chat_id = '" + str(chat_id) +"' and t.year = " + str(year)
    cursor.execute(select)
    team_ids = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##team_ids = db.query(select)
    return team_ids[0][0]

def getgameidbyteamid(team_id, date):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select distinct (g.id_game) from games g, reg_users u, ready2play r where  g.date IS NOT NULL and g.date = r.date and r.date = '" + str(date) + "' and (g.id_team_one = " + str(team_id) + " or g.id_team_two = " + str(team_id) + ")"
    cursor.execute(select)
    game_ids = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##game_ids = db.query(select)
    if game_ids:
        return game_ids[0][0]
    else:
        return None

def getfullnamebychatid(chat_id):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select full_name from reg_users where chat_id = '" + str(chat_id) + "'"
    cursor.execute(select)
    first_names = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##first_names = db.query(select)
    return first_names[0][0]

def getwhoisready(year, date, state):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    select = "select distinct t.team_id, t.team_name, t.team_emoji, u.full_name from teams t,  reg_users u, ready2play r where t.full_name = u.full_name and t.year = " + str(year) + " and r.date = '"+ str(date) + "' and u.chat_id in (select chat_id from ready2play where is_ready = " + str(state) + " and date = '" + str(date) + "') order by t.team_id"
    cursor.execute(select)
    ready_teams = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##ready_teams = db.query(select)
    return ready_teams

def getallplayedgames(year, team = None):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    if not team:
        select = """
    select g.id_game, t1.team_name, g.goals_one, t1.team_emoji, t2.team_name, g.goals_two, t2.team_emoji, g.date, g.tour, g.tg_file_id from games g
    inner join teams t1 ON g.id_team_one=t1.team_id
    inner join teams t2 ON g.id_team_two=t2.team_id
    where t1.year = """ + str(year) + """ and g.goals_one > -1 and g.tg_file_id IS NOT NULL order by g.tour, g.id_game
    """
    else:
        select = """
        select g.id_game, t1.team_name, g.goals_one, t1.team_emoji, t2.team_name, g.goals_two, t2.team_emoji, g.date, g.tour, g.tg_file_id from games g
        inner join teams t1 ON g.id_team_one=t1.team_id
        inner join teams t2 ON g.id_team_two=t2.team_id
        where t1.year = """ + str(year) + """ and (t1.team_name = '""" + team + """' or t2.team_name = '""" + team + """') and g.tg_file_id IS NOT NULL order by g.tour, g.id_game
        """
    cursor.execute(select)
    matches = cursor.fetchall()
    conn.commit()
    cursor.close()
    ##matches = db.query(select)
    return matches

# added 02.04.2018 for get opponent video

# end 02.04.2018

def insvideoid(game_id, video_id):
    conn, cursor = dbconnect()
    ##db = dbconnect()
    update = "UPDATE .games SET tg_file_id = '" + str(video_id) + "' WHERE id_game = " + str(game_id)
    cursor.execute(update)
    conn.commit()
    cursor.close()
    ##db.query(update)

def print_table(table):
    col_width = [max(len(x) for x in col) for col in zip(*table)]
    for line in table:
        print("| " + " | ".join("{:{}}".format(x, col_width[i])
                                for i, x in enumerate(line)) + " |")
