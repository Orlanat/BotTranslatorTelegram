from tb_static import TB
from db_static import DB
from bot_logic import generate_test_question
from bot_keyboard import BotKeyboard
from telebot import types
from datetime import datetime
from bot_logic import add_user

bot = TB.get()
conn = DB.get()


class bot_translator:
    @staticmethod
    def processing(message):
        print(message)
        if 'callback_query' in message:
            text = message["callback_query"]["data"]
            user_id = message["callback_query"]['message']['chat']['id']
            user_name = "ErrorName"

        if 'message' in message:
            user_id = message['message']['chat']['id']
            user_name = "ErrorName"
            if 'username' in message['message']['chat']:
                user_name = message['message']['chat']['username']

            if 'first_name' in message['message']['chat']:
                user_name = message['message']['chat']['first_name']

            print(f"user_name: {user_name}")

            if 'text' not in message['message']:
                bot.send_message(user_id, f"Опять за старое взялся? {user_name}!", reply_markup=BotKeyboard.start_keyboard())
                return
            text = message['message']['text']

            if "reply_markup" in message['message']:
                text = message['message']["reply_markup"][0]["callback_data"]

            print(f"text: {text}")

        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
        row = cur.fetchone()
        if row is None:
            add_user(user_id, user_name)
            #bot.send_message(user_id, f"Привет {user_name}",
            #                 reply_markup=BotKeyboard.start_keyboard())
            print("jasdhjdsahdkjashdkjsahdkjashdkjahsdkjahskjdhashdkjasksdajah")
            conn.commit()
            return

        cur = conn.cursor()
        cur.execute(f"SELECT state FROM users WHERE id = {user_id} ")
        row = cur.fetchone()

        if row[0] == 0:
            if '/start' == text:
                bot.send_message(user_id, f"Привет {user_name}",
                                 reply_markup=BotKeyboard.start_keyboard())
                pass
            elif 'Начать тест' == text:
                start_test(conn, user_id)
                pass
            elif 'Статистика' == text:
                get_statistic(conn, user_id)
                pass
            elif 'Настройка параметров' == text:
                bot.send_message(user_id, f"Настройка параметров",
                                 reply_markup=BotKeyboard.setting_keyboard())
                pass
            elif 'Увеличить сложность' == text:
                complexity_add(conn, user_id, 1)
            elif 'Уменьшить сложность' == text:
                complexity_add(conn, user_id, -1)
            elif 'Увеличить повторения' == text:
                question_add(conn, user_id, 1)
                pass
            elif 'Уменьшить повторения' == text:
                question_add(conn, user_id, -1)
                pass
            elif 'Сменить тему' == text:
                theme_options(conn, user_id)
                pass
            elif 'Тема: ' in text:
                switch_theme(conn, user_id, text)
                pass
        if row[0] == 1:
            if 'Ответ: ' in text:
                answer_processing(conn, user_id, text)
                print(f"oTVET {bot} {text} {user_id}")
            elif 'Остановить тест' == text:
                stop_test(conn, user_id)
            else:
                # Echo test without logic
                print(f"{bot} {text} {user_id}")
                #bot.send_message(user_id, f"Эхо: {text}", reply_markup=BotKeyboard.start_keyboard())
                text = generate_test_question(conn, user_id)
                #bot.send_message(user_id, f"Тестовый вопрос: {text}", reply_markup=BotKeyboard.start_keyboard())
                # delete_all_progress_users(conn)
        else:
            bot.send_message(user_id, f"Привет {user_name}")



def theme_options(conn, user_id):
    cur = conn.cursor()
    cur.execute('SELECT theme FROM themes')
    themes = []
    for row in cur:
        themes.append(row[0])
    bot.send_message(user_id, "Выберите тему", reply_markup=BotKeyboard.theme_keyboard(themes))


def switch_theme(conn, user_id, text):
    theme = text.split(f'Тема: ')
    theme = theme[1]
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM themes WHERE theme = '{theme}'")

    row = cur.fetchone()
    if row is None:
        return

    cur.execute(f"UPDATE users SET theme = {row[0]} WHERE id = {user_id}")
    conn.commit()
    bot.send_message(user_id, "Тема изменена", reply_markup=BotKeyboard.start_keyboard())


def complexity_add(conn, user_id, delta):
    cur = conn.cursor()
    cur.execute(f"SELECT complexity FROM users WHERE id = {user_id}")
    row = cur.fetchone()
    if row is None:
        return
    complexity = row[0] + delta
    if complexity > 3:
        complexity = 3
    if complexity < 2:
        complexity = 2

    cur.execute(f"UPDATE users SET complexity = {complexity} WHERE id = {user_id}")
    conn.commit()
    bot.send_message(user_id, "Сложность изменена", reply_markup=BotKeyboard.start_keyboard())


def question_add(conn, user_id, delta):
    cur = conn.cursor()
    cur.execute(f"SELECT max_question FROM users WHERE id = {user_id}")
    row = cur.fetchone()
    if row is None:
        return
    max_question = row[0] + delta
    if max_question > 10:
        max_question = 10
    if max_question < 3:
        max_question = 3

    cur.execute(f"UPDATE users SET max_question = {max_question} WHERE id = {user_id}")
    conn.commit()
    bot.send_message(user_id, f"Текущее количество вопросов тесте: {max_question}", reply_markup=BotKeyboard.start_keyboard())


def delete_all_progress_users(conn):
    curr = conn.cursor()
    curr.execute("DELETE FROM users")
    curr.execute("DELETE FROM progress")
    conn.commit()


def start_test(conn, user_id):
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET num_questions = 1, rating = 0, state = 1 WHERE id = {user_id} ")
    generate_question(conn, user_id)
    conn.commit()


def stop_test(conn, user_id):
    cur = conn.cursor()
    cur.execute(f"SELECT rating, max_question FROM users WHERE id = {user_id}")
    row = cur.fetchone()
    if row is None:
        return

    bot.send_message(user_id, f"Тест завершен")
    bot.send_message(user_id, f"Правильность на {row[0]} из {row[1]}", reply_markup=BotKeyboard.start_keyboard())

    cur.execute(f"UPDATE users SET state = 0, last_date = '{datetime.today()}' WHERE id = {user_id} ")

    conn.commit()


def answer_processing(conn, user_id, text):
    cur = conn.cursor()
    cur.execute(f'SELECT num_questions, max_question FROM users WHERE id = {user_id}')
    row = cur.fetchone()

    if row is None:
        return

    if f'{row[0]}. Ответ: ' not in text:
        return

    words = text.split(f'{row[0]}. Ответ: ')
    print(words)
    words = words[1].split(': ')
    print(words)
    res = check_answer(conn, user_id, words[0], words[1])
    # bot.send_message(user_id, res, reply_markup=BotKeyboard.start_keyboard())

    if row[0] == row[1]:
        bot.send_message(user_id, res, reply_markup=BotKeyboard.start_keyboard())
        stop_test(conn, user_id)
    else:
        num_add(conn, user_id, 1)
        bot.send_message(user_id, res)
        generate_question(conn, user_id)


def num_add(conn, user_id, delta):
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET num_questions = num_questions + {delta} WHERE id = {user_id} ")
    conn.commit()


def generate_question(conn, user_id):
    q = generate_test_question(conn, user_id)
    if q != -1:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        print(q)
        keyboard = []
        row=[]
        for options in q["Answer options"]:
            #markup.add(types.KeyboardButton(options))
            words = options.split(': ')
            row.append(types.InlineKeyboardButton(text=words[2], callback_data=options))
            keyboard.append(row)
            row=[]
        markup.add(types.KeyboardButton('Остановить тест'))
        choice = types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(text="Отмена", callback_data="Остановить тест")
                ]
            ]
        )
        choice = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(user_id, q["Question"], reply_markup=choice)
        bot.send_message(user_id, q["Question"], reply_markup=markup)


def check_answer(conn, user_id, word_en, word_ru):
    curr = conn.cursor()
    curr.execute(f"SELECT id, word FROM users WHERE id = {user_id}")
    row_user = curr.fetchone()
    res = ''

    # если пользователь найден
    if row_user is not None:
        curr.execute(f"SELECT id FROM words WHERE en = '{word_en}' AND ru = '{word_ru}'")
        row_word = curr.fetchone()
        # если слово найдено в таблице
        if row_word is not None:
            res = "Красавчик"
            print("Красавчик")
            curr.execute(
                f"UPDATE progress SET grade = grade + 1, last_date = '{datetime.today()}' WHERE user_id = {row_user[0]} AND word = {row_word[0]}")
            curr.execute(
                f"UPDATE users SET rating = rating + 1, last_date = '{datetime.today()}' WHERE id = {user_id}")

        else:
            res = "Нетушки"

            # Reset progress en word
            curr.execute(f"SELECT id FROM words WHERE en = '{word_en}'")
            row_word = curr.fetchone()
            if row_word is None:
                return
            curr.execute(
                f"UPDATE progress SET grade = 0 WHERE user_id = {row_user[0]} AND word = {row_word[0]}")

            # Reset progress ru word
            curr.execute(f"SELECT id FROM words WHERE ru = '{word_ru}'")
            row_word = curr.fetchone()
            if row_word is None:
                return
            curr.execute(
                f"UPDATE progress SET grade = 0 WHERE user_id = {row_user[0]} AND word = {row_word[0]}")

    conn.commit()
    return res


def get_statistic(conn, user_id):
    curr = conn.cursor()
    curr.execute('SELECT users.id, users.first_name, users.grade, ' +
                 'themes.theme, AVG(progress.grade) AS avg_progress_grade ' +
                 'FROM users ' +
                 f'INNER JOIN progress ON progress.user_id = {user_id} ' +
                 'INNER JOIN words ON words.id = progress.word ' +
                 'INNER JOIN themes ON themes.id = words.theme ' +
                 f'WHERE users.id = {user_id} '
                 f'GROUP BY users.id, users.first_name, users.grade, themes.theme ')
    row = curr.fetchone()
    if row is None:
        return
    bot.send_message(user_id, f'Пользователь: {row[1]}', reply_markup=BotKeyboard.start_keyboard())
    bot.send_message(user_id, f'Тема: {row[3]}  — {"{0:.2f}".format(row[4] / row[2] * 100)} %',
                     reply_markup=BotKeyboard.start_keyboard())
    print(f'Тема: {row[3]}  — {"{0:.2f}".format(row[4] / row[2] * 100)} %')
    for row in curr:
        print(f'Пользователь: {row[1]}')
        bot.send_message(user_id, f'Тема: {row[3]}  — {"{0:.2f}".format(row[4]/row[2] * 100) } %',
                         reply_markup=BotKeyboard.start_keyboard())



