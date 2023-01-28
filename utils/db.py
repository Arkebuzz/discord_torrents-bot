import json
import os
import sqlite3

from config import PATH_DB as PATH


def create_db(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS games(
           name TEXT PRIMARY KEY, 
           img TEXT,
           user_id INTEGER,
           messages_id TEXT,
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


def game_guild_settings(guild_id, channel_id, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM guilds WHERE id = ?;', (guild_id,))
        res = cur.fetchall()

        if res:
            cur.execute('UPDATE guilds SET channel_id = ? WHERE id = ?;', (guild_id, channel_id))
        else:
            cur.execute('INSERT INTO guilds VALUES(?, ?);', (guild_id, channel_id))

        conn.commit()


def get_guilds(gid=None, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        if gid is None:
            cur.execute('SELECT * FROM guilds;')
        else:
            cur.execute('SELECT * FROM guilds WHERE id = ?;', (gid,))

        res = cur.fetchall()

        return res


def check_game(name, d_name, path=PATH):
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


def new_game(name, img, user_id, mes_id, d_name, version, genre, gtype, sys, description, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_added FROM users WHERE user_id = ?;', (user_id,))
        res = cur.fetchall()
        if len(res) == 0:
            cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);', (user_id, 1, 0, 0))
        else:
            cur.execute('UPDATE users SET num_added = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute(
            'INSERT INTO games VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, "{}");',
            (name, img, user_id, mes_id, d_name, version, genre, gtype, sys, description))

        conn.commit()


def search_game(name=None, genre=None, gtype=None, path=PATH):
    """
    Поиск игр по названию, типу или жанру, если параметры не переданы, выводит все игры.
    :param name:
    :param genre:
    :param gtype:
    :param path:
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


def add_reaction(mes, user_id, react, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute(
            'SELECT user_voted, name FROM games '
            f'WHERE messages_id LIKE "%{mes}%";'
        )
        res = cur.fetchall()

        if not res:
            return

        users, name = res[0]
        users = json.loads(users)

        if str(user_id) not in users:
            cur.execute('SELECT num_votes FROM users WHERE user_id = ?', (user_id, ))
            num = cur.fetchall()[0][0]
            cur.execute('UPDATE users SET num_votes = ? WHERE user_id = ?;',
                        (num + 1, user_id))

        users[str(user_id)] = react

        cur.execute('UPDATE games SET user_voted = ? WHERE name = ?;',
                    (json.dumps(users), name))

        conn.commit()


def del_reaction(mes, user_id, react, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute(
            'SELECT user_voted, name FROM games '
            f'WHERE messages_id LIKE "%{mes}%";'
        )
        res = cur.fetchall()

        if not res:
            return

        users, name = res[0]
        users = json.loads(users)

        if users.setdefault(str(user_id), -1) == react:
            del users[str(user_id)]

            cur.execute('UPDATE games SET user_voted = ? WHERE name = ?;',
                        (json.dumps(users), name))

            cur.execute('SELECT num_votes FROM users WHERE user_id = ?', (user_id, ))
            num = cur.fetchall()[0][0]
            cur.execute('UPDATE users SET num_votes = ? WHERE user_id = ?;',
                        (num - 1 if num > 0 else 0, user_id))

        conn.commit()


def new_download(game_n, user_id, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_downloads FROM users WHERE user_id = ?;', (user_id,))
        res = cur.fetchall()
        cur.execute('UPDATE users SET num_downloads = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute('SELECT num_downloads FROM games WHERE name = ?;', (game_n,))
        res = cur.fetchall()
        cur.execute('UPDATE games SET num_downloads = ? WHERE name = ?;', (res[0][0] + 1, game_n))

        conn.commit()


def top_games(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT name, num_downloads, user_voted FROM games;')
        res = [(d, sum(json.loads(s).values()) / len(json.loads(s)) if json.loads(s) else 0, n) for n, d, s in
               cur.fetchall()]

        return sorted(res, reverse=True)[:5]


def top_users(path=PATH):
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

        cur.execute('SELECT * FROM users;')
        res = cur.fetchall()

        print(res)


if __name__ == '__main__':
    print(os.getcwd())
    test()
