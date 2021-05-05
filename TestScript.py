import sqlite3
import telebot
from telebot import types
import random

bot = telebot.TeleBot('token')

def findNameWithID(id):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        row = cur.execute("SELECT * FROM sqlitedb_developers WHERE id = ?", (id, ))
    return next(row)

print(findNameWithID(1795726860)[1])