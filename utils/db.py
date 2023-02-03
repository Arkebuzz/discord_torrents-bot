import json
import os
import sqlite3

from config import PATH_DB as PATH


def create_db(path=PATH):
    """
    Создаёт БД по пути path.

    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS games(
           name TEXT PRIMARY KEY, 
           img TEXT,
           user_id INTEGER,
           dir_name TEXT,
           version TEXT,
           genre TEXT,
           type TEXT,
           sys_requirements TEXT,
           description TEXT,
           num_downloads INTEGER,
           user_voted TEXT);
           ''')
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
           user_id INTEGER PRIMARY KEY,
           num_added INTEGER,
           num_downloads INTEGER,
           num_votes INTEGER);
           ''')
        cur.execute('''CREATE TABLE IF NOT EXISTS guilds(
           id INTEGER PRIMARY KEY,
           channel_id INTEGER);
           ''')

        conn.commit()


def update_guild_settings(guild_id, channel_id, path=PATH):
    """
    Обновляет настройки канала сервера.

    :param guild_id: ID сервера.
    :param channel_id: Новое ID канала.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM guilds WHERE id = ?;', (guild_id,))
        res = cur.fetchall()

        if res:
            cur.execute('UPDATE guilds SET channel_id = ? WHERE id = ?;', (guild_id, channel_id))
        else:
            cur.execute('INSERT INTO guilds VALUES(?, ?);', (guild_id, channel_id))

        conn.commit()


def guild_remove(guild_id, path=PATH):
    """
    Удаление сервер из БД.

    :param guild_id: ID сервера.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('DELETE FROM guilds WHERE id = ?;', (guild_id,))

        conn.commit()


def get_guilds(gid=None, path=PATH):
    """
    Возвращает сервера бота c введенным ID, если ID не передан, то возвращает все сервера.

    :param gid: ID сервера.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        if gid is None:
            cur.execute('SELECT * FROM guilds;')
        else:
            cur.execute('SELECT * FROM guilds WHERE id = ?;', (gid,))

        res = cur.fetchall()

        return res


def check_game(name, d_name, path=PATH):
    """
    Проверяет наличие игры в БД по названию и пути.

    :param name: Название игры.
    :param d_name: Путь к игре.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM games WHERE name = ?;', (name,))
        name = cur.fetchall()
        cur.execute('SELECT * FROM games WHERE dir_name = ?;', (d_name,))
        d_name = cur.fetchall()

        if len(name):
            return name
        if len(d_name):
            return d_name[0][0]
        return False


def new_game(name, img, user_id, d_name, version, genre, gtype, sys, description, path=PATH):
    """
    Добавляет новую игры в БД.

    :param name: Название игры.
    :param img: Адрес фото игры.
    :param user_id: ID пользователя, добавившего игру.
    :param d_name: Путь к файлам игры.
    :param version: Версия игры.
    :param genre: Жанры игры.
    :param gtype: Типы игра.
    :param sys: Системные требования игры.
    :param description: Описание игры.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_added FROM users WHERE user_id = ?;', (user_id,))
        res = cur.fetchall()
        if len(res) == 0:
            cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);', (user_id, 1, 0, 0))
        else:
            cur.execute('UPDATE users SET num_added = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute(
            'INSERT INTO games VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, 0, "{}");',
            (name, img, user_id, d_name, version, genre, gtype, sys, description))

        conn.commit()


def search_game(name=None, genre=None, gtype=None, path=PATH):
    """
    Поиск игр по названию, типу или жанру, если параметры не переданы, выводит все игры.

    :param name: Название игры.
    :param genre: Жанры игры.
    :param gtype: Типы игры.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        if name is not None:
            cur.execute(f'SELECT * FROM games WHERE name LIKE "%{name}%";')
            res = cur.fetchall()

        elif genre is not None:
            res = set()
            for i in genre:
                cur.execute(f'SELECT * FROM games WHERE genre LIKE "%{i}%";')
                for j in cur.fetchall():
                    res.add(j)

        elif gtype is not None:
            res = set()
            for i in gtype:
                cur.execute(f'SELECT * FROM games WHERE type LIKE "%{i}%";')
                for j in cur.fetchall():
                    res.add(j)

        else:
            cur.execute('SELECT * FROM games;')
            res = cur.fetchall()

        return list(res)


def add_reaction(name, user_id, react, path=PATH):
    """
    Добавление отзыва к игре.

    :param name: Название игры.
    :param user_id: ID пользователя.
    :param react: Отзыв.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute(f'SELECT user_voted FROM games WHERE name = ?;', (name,))
        res = cur.fetchall()

        if not res:
            return

        users = json.loads(res[0][0])

        if str(user_id) not in users:
            cur.execute('SELECT num_votes FROM users WHERE user_id = ?;', (user_id,))
            res = cur.fetchall()
            if len(res) == 0:
                cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);', (user_id, 0, 0, 1))
            else:
                cur.execute('UPDATE users SET num_votes = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        users[str(user_id)] = react

        cur.execute('UPDATE games SET user_voted = ? WHERE name = ?;',
                    (json.dumps(users), name))

        conn.commit()


def new_download(game_n, user_id, path=PATH):
    """
    Обновляет данные о количестве загрузок игры и пользователя.

    :param game_n: Название игры.
    :param user_id: ID пользователя.
    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_downloads FROM users WHERE user_id = ?;', (user_id,))
        res = cur.fetchall()
        if len(res) == 0:
            cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);', (user_id, 0, 1, 0))
        else:
            cur.execute('UPDATE users SET num_downloads = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute('SELECT num_downloads FROM games WHERE name = ?;', (game_n,))
        res = cur.fetchall()
        cur.execute('UPDATE games SET num_downloads = ? WHERE name = ?;', (res[0][0] + 1, game_n))

        conn.commit()


def top_games(path=PATH):
    """
    Возвращает все игры, отсортированные в порядке убывания скачиваний и комментариев.

    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT name, num_downloads, user_voted FROM games;')
        games = []
        for name, down, votes in cur.fetchall():
            votes = json.loads(votes)
            sc = 0

            for vote in votes:
                sc += int(votes[vote][0])

            score = sc / len(votes) if votes else 0

            games.append((score, down, name))
        return sorted(games, reverse=True)[:5]


def top_users(path=PATH):
    """
    Возвращает всех пользователей в порядке убывания активности с ботом.

    :param path: Путь к БД.
    :return:
    """

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM users;')
        res = cur.fetchall()

        return sorted(res, reverse=True, key=key4users)[:5]


def key4users(a):
    return a[1] * 3 + a[2] + a[3] * 2


def test(path='../media/game.db'):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        print('_______________________')

        print('users')
        cur.execute('SELECT * FROM users;')
        print(*cur.fetchall(), sep='\n', end='\n_______________________\n')

        print('games')
        cur.execute('SELECT * FROM games;')
        print(*cur.fetchall(), sep='\n', end='\n_______________________\n')

        print('guilds')
        cur.execute('SELECT * FROM guilds;')
        print(*cur.fetchall(), sep='\n')


if __name__ == '__main__':
    test()
