import sqlite3
import telebot
from telebot import types
import random

bot = telebot.TeleBot('1795726860:AAHVQZgmXGW-ns5Xqp349yt53A-6NgefToI')

def findNameWithID(userid):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        row = cur.execute("SELECT * FROM sqlitedb_developers WHERE id ="+userid+"")
    return next(row)

print(findNameWithID(998544674))