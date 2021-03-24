# web: gunicorn app:app
# worker: python main.py 5000
# heroku addons:create heroku-postgresql:hobby-dev
# Created postgresql-metric-65240 as DATABASE_URL
# pip install psycopg2-binary

# import os
import psycopg2
import datetime
import json


class BotDataBase:
    conn = -1
    cur = -1

    @staticmethod
    def connect():
        # DATABASE_URL = os.environ['postgresql-metric-65240']
        # BotDataBase.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        BotDataBase.conn = psycopg2.connect(database="dfh4u9ku9r591a",
                                            user="pihbteuhurzhje",
                                            password="0318a7704a9234b8744cba962b1b1a63b919d5a87d4810b4810f299794749ae8",
                                            host="ec2-52-71-161-140.compute-1.amazonaws.com",
                                            port=5432)
        BotDataBase.cur = BotDataBase.conn.cursor()
        pass

    @staticmethod
    def tb_users():
        BotDataBase.cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, " +
                                "first_name VARCHAR(64), " +
                                "state INTEGER," +
                                "theme INTEGER," +
                                "complexity INTEGER," +
                                "grade INTEGER," +
                                "num_questions INTEGER)")
        BotDataBase.conn.commit()

    @staticmethod
    def tb_themes():
        BotDataBase.cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, " +
                                "theme VARCHAR(64))")
        BotDataBase.conn.commit()

    @staticmethod
    def tb_words():
        BotDataBase.cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, " +
                                "theme INTEGER, " +
                                "en VARCHAR(64)," +
                                "ru VARCHAR(64))")
        BotDataBase.conn.commit()

    @staticmethod
    def tb_states():
        BotDataBase.cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, " +
                                "state INTEGER")
        BotDataBase.conn.commit()

    @staticmethod
    def tb_progress():
        BotDataBase.cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, " +
                                "user INTEGER, " +
                                "word INTEGER," +
                                "grade INTEGER,"
                                "last_date DATE)")
        BotDataBase.conn.commit()

    @staticmethod
    def add_user(json):
        id = json['message']['chat']['id']
        first_name = json['message']['chat']['first_name']
        BotDataBase.cur.execute("INSERT INTO users (id, first_name, state, theme, complexity, grade, num_questions) " +
                                "VALUES (%i, %s, %i, %i, %i, %i, %i)",
                                (id, first_name, 1, 1, 3, 3, 3))
        BotDataBase.conn.commit()
        BotDataBase.cur.execute("SELECT id FROM words")
        for row in BotDataBase.cur:
            user = id
            word = row["id"]
            BotDataBase.add_progress(user, word)

    @staticmethod
    def add_theme(theme):
        BotDataBase.cur.execute("INSERT INTO themes (theme) " +
                                "VALUES (%s)",
                                (theme))
        BotDataBase.conn.commit()

    @staticmethod
    def add_word(theme, en, ru):
        BotDataBase.cur.execute("INSERT INTO words (theme, en, ru) " +
                                "VALUES (%s, %s, %s)",
                                (theme, en, ru))
        BotDataBase.conn.commit()

    @staticmethod
    def add_progress(user, word):
        BotDataBase.cur.execute("INSERT INTO progress (user, word, grade, last_date) " +
                                "VALUES (%i, %i, %i, %d)",
                                (user, word, 0, datetime.today()))
        BotDataBase.conn.commit()

    @staticmethod
    def add_themes_and_words(dir):
        with open(dir, "r", encoding="utf-8") as f:
            js = json.load(f)
            themes = []
            for p in js["progress"]:
                BotDataBase.add_theme(p["Theme"])
                BotDataBase.cur.execute(f"SELECT id FROM themes WHERE theme = {p['Theme']}")
                row = BotDataBase.cur.fetchone()
                theme_id = row[0]
                for word in p["Words"]:
                    BotDataBase.add_word(theme_id, word['EN'], word['RU'])

    @staticmethod
    def init():
        BotDataBase.tb_users()
        BotDataBase.tb_words()
        BotDataBase.tb_states()
        BotDataBase.tb_themes()
        BotDataBase.tb_progress()
        BotDataBase.add_themes_and_words()

