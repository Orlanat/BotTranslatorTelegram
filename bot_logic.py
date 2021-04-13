import random
from datetime import datetime

from tb_static import TB
from db_static import DB

bot = TB.get()
conn = DB.get()


def generate_test_question(conn, user_id):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user_row = cur.fetchone()

    # Pls delete this
    if user_row is None:
        add_user(user_id, "TestName")
        cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
        user_row = cur.fetchone()

    # Найти слова по теме
    words = get_words(user_row)
    if words == -1:
        return -1
    # Создать вопрос и варианты ответов
    random.shuffle(words)
    index = 0
    o = []
    grade = user_row[5]
    complexity = user_row[4]
    for word in words:
        index += 1
        if word["grade"] < grade:
            q = f"Переведите: {word['EN']}"
            o.append(f"{word['EN']}: {word['RU']}")
            i = 1
            while i < complexity:
                o.append(f"{word['EN']}: {words[(index + i + 2) % len(words)]['RU']}")
                i += 1
            random.shuffle(o)
            res = {"Question": q, "Answer options": o}
            return res
    else:
        return -1


def get_words(user_row):
    print(user_row)
    if user_row is None:
        return -1
    theme = user_row[3]
    words = []
    cur = conn.cursor()
    cur.execute(f"SELECT en, ru FROM words WHERE theme = {theme}")
    for row in cur:
        words.append({'EN': row[0], 'RU': row[1]})
    print(f"Words: {words}")
    return words


def add_user(id, first_name):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE id = {id}")
    row = cur.fetchone()
    if row is not None:
        return
    cur.execute("INSERT INTO users (id, first_name, state, theme, complexity, grade, num_questions) " +
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (id, first_name, 1, 1, 3, 3, 3))
    conn.commit()
    cur.execute("SELECT id FROM words")
    for row in cur:
        word_id = row[0]
        print(word_id)
        user_id = id
        add_progress(user_id, word_id)
    cur.execute("SELECT * FROM users")
    for row in cur:
        print(row)


def add_progress(user, word):
    cur = conn.cursor()
    cur.execute("INSERT INTO progress (user_id, word, grade, last_date) " +
                "VALUES (%s, %s, %s, %s)",
                (user, word, 0, datetime.now()))
    conn.commit()