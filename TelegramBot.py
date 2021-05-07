import telebot
from telebot import types
import sqlite3
import random
import time
import logging

bot = telebot.TeleBot('token')

name = ''
nick = ''
age = 0


# Меняет никнейм пользователя
def editUserNick(nickname, id):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute('UPDATE personalData SET nickname = ? WHERE userid = ?', (nickname, id))
        con.commit()
    writeInLog(foundNameWithID(id)[1] + ' изменил никнейм пользователя на ' + nickname)


# Меняет Имя пользователя
def editUserName(name, id):
    user_info = foundNameWithID(id)
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute('UPDATE personalData SET name = ? WHERE userid = ?', (name, id))
        con.commit()
    writeInLog(foundNameWithID(id)[1] + ' изменил имя пользователя на ' + name + '.')


# Меняет возраст пользователя
def editUserAge(age, id):
    user_info = foundNameWithID(id)
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute('UPDATE personalData SET age = ? WHERE userid = ?', (age, id))
        con.commit()
    writeInLog(user_info[1] + ' (' + user_info[3] + ') изменил возраст на ' + age + '. Старый возраст - ' +
               user_info[3])


# Конвертируем из секунд в часы, минуты, секунды (в массив)
def format_duration(seconds):
    if seconds <= 0:
        return 'Готов!'
    resultTime = [seconds, 0, 0]
    for i in range(1, 3):
        resultTime[i] = resultTime[i - 1] // 60
        resultTime[i - 1] -= resultTime[i] * 60
    return resultTime


# Существует ли позователь с таким ID? True/False
def thisUserExistToID(id):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute("SELECT rowid FROM personalData WHERE userid = ?", (id,))
        data = cur.fetchall()
        if len(data) == 0:
            return False
        else:
            return True


# Существует ли позователь с таким Именем? True/False
def thisUserExistToName(name):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute("SELECT rowid FROM personalData WHERE nickname = ?", (name,))
        data = cur.fetchall()
        if len(data) == 0:
            return False
        else:
            return True


# Передача поинтов
def presentPoints(idRecipient, idSender, points):
    minusPoints(idSender, points)
    plusPoints(idRecipient, points)
    bot.send_message(idSender, 'Посылка передана! Ваш баланс ' + str(foundNameWithID(idSender)[4]))
    # bot.send_message(idRecipient, 'Вы получили подарок (' + points + '). Ваш баланс ' + str(foundNameWithID(idRecipient)[4]))
    writeInLog(str(foundNameWithID(idRecipient)[1]) + ' получил ' + points + ' от ' + str(foundNameWithID(idSender)[1]))


# Записываем в файл на пк нужную нам информауию(message) со временем
def writeInLog(message):
    logging.basicConfig(filename='log.log', filemode='w', level=logging.INFO, format='%(asctime)s : %(message)s | %('
                                                                                     'levelname)s')
    logging.info(message)


# Добавляет в БД новую строку с данными
def addInDB(id, name, nick, age):
    if name == '' and nick == '':
        with sqlite3.connect("TestTGBotDataBase.db") as con:
            cur = con.cursor()
            timenow = int(time.time())
            cur.execute("INSERT INTO personalData VALUES (?, ?, ?, ?, ?, ?)", (id, nick, name, age, 100, timenow))
            con.commit()
            writeInLog("Добавлен новый пользователь ID: " + str(id) + " Name: " + name + " User Name: " + nick +
                   " Age: " + str(age))
    else:
        bot.send_message(id, 'Попробуй заного. Напиши /reg')


# Возвращает строку с пользователем по Имени пользователя
def foundNameWithNickName(nick):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        row = cur.execute("SELECT * FROM personalData WHERE nickname = ?", (nick,))
    return next(row)


# Возвращает строку с пользователем по id
def foundNameWithID(id):
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        row = cur.execute("SELECT * FROM personalData WHERE userid = ?", (id,))
    return next(row)


# Забирает очки у пользователя по id
def minusPoints(id, points):
    user = foundNameWithID(id)
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute(
            f'UPDATE personalData SET score = {user[4] - int(points)} WHERE userid = {id}')
        con.commit()


# Функция выдаёт очки пользователю по id
def plusPoints(id, points):
    user = foundNameWithID(id)
    with sqlite3.connect("TestTGBotDataBase.db") as con:
        cur = con.cursor()
        cur.execute(
            f'UPDATE personalData SET score = {user[4] + int(points)} WHERE userid = {id}')
        con.commit()


# На вход получает массив из [сек, мин, час] и возвтращает с расшифровкой
def BonusTime(timeToBonus):
    if timeToBonus == 'Готов!':
        return timeToBonus
    message = ''
    if timeToBonus[2] > 0:
        message += 'Часы: ' + str(timeToBonus[2]) + ' '
    if timeToBonus[1] > 0:
        message += 'Минуты: ' + str(timeToBonus[1]) + ' '
    if timeToBonus[0] > 0:
        message += 'Секунды: ' + str(timeToBonus[0]) + ' '
    return message


# Пользователь может забрать бонус раз в день (86400 секунд)
def takeBonus(id):
    if (time.time() - foundNameWithID(id)[5]) > 86400:
        user = foundNameWithID(id)
        with sqlite3.connect("TestTGBotDataBase.db") as con:
            cur = con.cursor()
            cur.execute(
                f'UPDATE personalData SET score = {user[4] + 100}, lasTime = {int(time.time())} WHERE userid = {id}')
            con.commit()
            bot.send_message(id, 'Вроде как должно придти, но не факт. Ты же меня знаешь)')
            writeInLog(str(user[1]) + 'получил бонус ')
    else:
        bot.send_message(id, 'Рано! До получания бонуса:\n' + BonusTime(format_duration(86400 -
                                                                                        (int(time.time()) - int(
                                                                                            foundNameWithID(id)[5])))))


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text.lower() == '/start' or message.text == 'Привет':
        if thisUserExistToID(message.chat.id):
            bot.send_message(message.chat.id, "Привет, " + foundNameWithID(message.chat.id)[
                1] + ". Это мой первый (не умерший на стадии запроса токена) бот на Python. Я собираюсь тут тестить и "
                     "изучать всякие фишки и добавлять новый функционал. Можешь написать /reg, чтобы занести свои "
                     "данные ко мне в базу))")
        else:
            bot.send_message(message.chat.id,
                             'Я посмортю, ты у нас тут в первый раз!? Круто! Это мой первый (не умерший на стадии '
                             'запроса токена) бот на Python. Я собираюсь тут тестить и изучать всякие фишки и '
                             'добавлять новый функционал. Можешь написать /reg, чтобы занести свои данные ко мне в '
                             'базу))')
    elif message.text.lower() == '/reg':
        if not thisUserExistToID(message.chat.id):
            bot.send_message(message.from_user.id, "Как тебя зовут?")
            bot.register_next_step_handler(message, get_name)  # следующий шаг – функция get_name
        else:
            user = foundNameWithID(message.chat.id)
            bot.send_message(message.chat.id,
                             'Ты уже зарегестрирован. Вот информация о тебе:\nNickname: ' + user[1] + '\nName: ' + user[
                                 2] + '\nAge: ' + str(user[3]) + '\nPoints: ' + str(user[4]))
    elif message.text.lower() == '/bonus':
        if thisUserExistToID(message.chat.id):
            takeBonus(message.chat.id)
        else:
            bot.send_message(message.from_user.id, "Похоже, ты не зарегестрирован. Давай, исправим. Как тебя зовут?")
            bot.register_next_step_handler(message, get_name)
    elif message.text.lower().split(' ')[0] == '/present':
        if thisUserExistToID(message.chat.id):
            usersPoints = foundNameWithID(message.chat.id)[4]
            splitMessage = message.text.split(' ')
            if len(splitMessage) != 3:
                bot.send_message(message.from_user.id, 'Ты где то ошибся, друг. Форма сообщения - /present {никнейм}(с '
                                                       'учётом регистра) {количество очков}, например: /present Qizo '
                                                       '100')
            else:
                if usersPoints >= int(splitMessage[2]):
                    if thisUserExistToName(splitMessage[1]):
                        presentPoints(foundNameWithNickName(splitMessage[1])[0], message.chat.id, splitMessage[2])
                    else:
                        bot.send_message(message.chat.id, 'Уточните имя пользоватеся, оно должно совпадать '
                                                          'досимвольно (с учётом регистра)')
                else:
                    bot.send_message(message.chat.id, 'Недостаточно средств. Ваш баланс: ' + str(usersPoints))
        else:
            bot.send_message(message.from_user.id, "Похоже, ты не зарегестрирован. Давай, исправим. Как тебя зовут?")
            bot.register_next_step_handler(message, get_name)
    elif message.text.split(' ')[0] == '/edit':
        if thisUserExistToID(message.chat.id):
            splitMessage = message.text.split(' ')
            errorMessage = 'Ты где то ошибся, друг. Форма сообщения - /edit {параметр, которовй хочешь изменить} {новое значение}, например: /edit age 20. Доступные для изменения данные: Nickname, Name, age '
            if len(splitMessage) != 3:
                bot.send_message(message.chat.id, errorMessage)
            elif splitMessage[1].lower() == 'nickname':
                if splitMessage[2].isalpha():
                    editUserNick(splitMessage[2], message.chat.id)
                    bot.send_message(message.chat.id, 'Новый никнейм установелен')
                else:
                    bot.send_message(message.chat.id, 'Неверный формат данных. Возраст должен содержать только буквы')
            elif splitMessage[1].lower() == 'age':
                try:
                    if 0 < int(splitMessage[2]) < 123:
                        editUserAge(splitMessage[2], message.chat.id)
                        bot.send_message(message.chat.id, 'Новый возраст установлен')
                    else:
                        bot.send_message(message.chat.id, 'Ты меня обманываешь!')
                except Exception:
                    bot.send_message(message.chat.id, 'Неверный формат данных. Возраст должен содержать только цинфры')
            elif splitMessage[1].lower() == 'name':
                if splitMessage[2].isalpha():
                    editUserName(splitMessage[2], message.chat.id)
                    bot.send_message(message.chat.id, 'Новое имя установлено')
                else:
                    bot.send_message(message.chat.id, 'Неверный формат данных. Возраст должен содержать только буквы')
            else:
                bot.send_message(message.chat.id, errorMessage)
        else:
            bot.send_message(message.from_user.id, "Похоже, ты не зарегестрирован. Давай, исправим. Как тебя зовут?")
            bot.register_next_step_handler(message, get_name)
    elif message.text.lower() == '/info':
        if (thisUserExistToID(message.chat.id)):
            timeForBonus = BonusTime(format_duration(86400 - (int(time.time()) -
                                                              int(foundNameWithID(message.chat.id)[5]))))
            user = foundNameWithID(message.chat.id)
            bot.send_message(message.chat.id,
                             'Ты уже зарегестрирован. Вот информация о тебе:\nНикнейм: ' + user[1] + '\nИмя: ' + user[
                                 2] + '\nВозраст: ' + str(user[3]) + '\nБаллы: ' + str(user[4]) + '\nСтатус бонуса: '
                             + timeForBonus)
        else:
            bot.send_message(message.from_user.id, "Похоже, ты не зарегестрирован. Давай, исправим. Как тебя зовут?")
            bot.register_next_step_handler(message, get_name)
    elif message.text.lower() == '/help':
        if thisUserExistToID(message.chat.id):
            bot.send_message(message.chat.id, 'Доступный функционал бота: \n'
                                              '/reg - зарегестрироваться в боте\n'
                                              '/bonus - Команда получения бонуса, доступно раз в 24 часа\n'
                                              '/present - подарить какому либо пользователю баллы. Форма сообщения - '
                                              '/present {никнейм}(с учётом регистра) '
                                              '{количество очков}, например: /present Qizo 100\n'
                                              '/edit - изменит какие либо данные о себе Форма сообщения - '
                                              '/edit {параметр, которовй хочешь изменить} {новое значение}, '
                                              'например: /edit age 20. '
                                              'Доступные для изменения данные: Nickname, Name, age\n'
                                              '/info - информация о профиле\n'
                                              'P.S. Все команды, кроме /reg не доступны новым пользователям, '
                                              'для начала необходимо зарегестрироваться')
        else:
            bot.send_message(message.chat.id, '')
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понял, прости, напиши /help, '
                                               'чтобы ознакомиться с командами, которые бот может воспринимать')


# Спрашиваем и получаем у пользователя его данные
def get_name(message):
    global name
    name = message.text
    if name.isalpha():
        bot.send_message(message.from_user.id, 'Придумай никнейм')
        bot.register_next_step_handler(message, get_nickname)
    else:
        bot.send_message(message.from_user.id, "Неверно введёные данные. В имени могут быть только буквы."
                                               " Напиши своё имя")
        bot.register_next_step_handler(message, get_name)


def get_nickname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global age
    if age == 0:  # проверяем что возраст изменился
        try:
            age = int(message.text)  # проверяем, что возраст введен корректно
            if age > 0 and age < 123:
                keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
                key_yes = types.InlineKeyboardButton(text='Верно', callback_data='yes')  # кнопка «Да»
                keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
                key_no = types.InlineKeyboardButton(text='Не верно', callback_data='no')
                keyboard.add(key_no)
                question = 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + '\nИмя пользователя ' + surname + '?'
                bot.send_message(message.chat.id, text=question, reply_markup=keyboard)
            else:
                bot.send_message(message.from_user.id, 'Не ври мне')
                bot.register_next_step_handler(message, get_age)
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
            bot.register_next_step_handler(message, get_age)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        try:
            addInDB(call.message.chat.id, name, surname, age)
            bot.send_message(call.message.chat.id, 'Запомню : )')
        except Exception:
            bot.send_message(call.message.chat.id, 'Что то пошло не так. Возможно это связано с тем, что вы пытаетесь '
                                                   'зарегестрироваться не первый раз')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Давай заново, напиши /reg')


bot.polling(none_stop=True, interval=0)
