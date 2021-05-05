import telebot
from telebot import types
import sqlite3
import random


bot = telebot.TeleBot('token')

name = ''
surname = ''
age = 0

def addInDB(id, name, surname, age):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO sqlitedb_developers VALUES (?, ?, ?, ?)", (id, name, surname, age))
        con.commit()
def findNameWithID(id):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        row = cur.execute("SELECT * FROM sqlitedb_developers WHERE id = ?", (id, ))
    return next(row)

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start' or message.text == 'Привет':
        try:
            bot.send_message(message.chat.id, "Привет, " + findNameWithID(message.chat.id)[1] + ". Это мой первый (не умерший на стадии запроса токена) бот на Python. Я собираюсь тут тестить и изучать всякие фишки и добавлять новый функционал. Можешь написать /reg, чтобы занести свои данные ко мне в базу))")
        except Exception:
            bot.send_message(message.chat.id,'Я посмортю, ты у нас тут в первый раз!? Круто! Это мой первый (не умерший на стадии запроса токена) бот на Python. Я собираюсь тут тестить и изучать всякие фишки и добавлять новый функционал. Можешь написать /reg, чтобы занести свои данные ко мне в базу))')
    elif message.text == '/reg':
        bot.send_message(message.from_user.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, get_name)  # следующий шаг – функция get_name
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg')


def get_name(message):  # получаем фамилию
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global age
    while age == 0:  # проверяем что возраст изменился
        try:
            age = int(message.text)  # проверяем, что возраст введен корректно
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + ' ' + surname + '?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        try:
            addInDB(call.message.chat.id, name, surname, age)
            bot.send_message(call.message.chat.id, 'Запомню : )')
        except Exception:
            bot.send_message(call.message.chat.id, 'Эй! Регестрироваться можно только 1 раз')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Давай заново, напиши /reg')


bot.polling(none_stop=True, interval=0)