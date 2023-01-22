import sqlite3

from config import PATH_DB as PATH


def create_db(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS games(
           game_name TEXT PRIMARY KEY,
           user_id INTEGER,
           dir_name TEXT,
           version TEXT,
           genre TEXT,
           type TEXT,
           sys_requirements TEXT,
           description TEXT,
           num_downloads INTEGER);
           ''')
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
           user_id INTEGER PRIMARY KEY,
           num_added INTEGER,
           num_downloads INTEGER);
           ''')
        conn.commit()


def check_game(name, d_name, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT * FROM games WHERE game_name = ?', (name,))
        name = cur.fetchall()
        cur.execute('SELECT * FROM games WHERE dir_name = ?', (d_name,))
        d_name = cur.fetchall()

        if len(name):
            return name
        if len(d_name):
            return d_name[0][0]
        return False


def new_game(user_id, name, d_name, version, genre, gtype, sys, description, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_added FROM users WHERE user_id = ?', (user_id,))
        res = cur.fetchall()
        if len(res) == 0:
            cur.execute('INSERT INTO users VALUES(?, ?, ?);', (user_id, 1, 0))
        else:
            cur.execute('UPDATE users SET num_added = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute(
            'INSERT INTO games VALUES(?, ?, ?, ?, ?, ?, ?, ?, 0);',
            (name, user_id, d_name, version, genre, gtype, sys, description))

        conn.commit()

        cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        print(cur.fetchall())


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
            cur.execute(f'SELECT * FROM games WHERE game_name LIKE "%{name}%"')
            res = cur.fetchall()

        elif genre is not None:
            res = set()
            for i in genre:
                cur.execute(f'SELECT * FROM games WHERE genre LIKE "%{i}%"')
                for j in cur.fetchall():
                    res.add(j)

        elif gtype is not None:
            res = set()
            for i in gtype:
                cur.execute(f'SELECT * FROM games WHERE type LIKE "%{i}%"')
                for j in cur.fetchall():
                    res.add(j)

        else:
            cur.execute('SELECT * FROM games')
            res = cur.fetchall()

        return list(res)


def new_download(game_n, user_id, path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_downloads FROM users WHERE user_id = ?', (user_id,))
        res = cur.fetchall()
        cur.execute('UPDATE users SET num_downloads = ? WHERE user_id = ?;', (res[0][0] + 1, user_id))

        cur.execute('SELECT num_downloads FROM games WHERE game_name = ?', (game_n,))
        res = cur.fetchall()
        cur.execute('UPDATE games SET num_downloads = ? WHERE game_name = ?;', (res[0][0] + 1, game_n))


def all_games(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_downloads, game_name  FROM games')
        res = cur.fetchall()

        return sorted(res, reverse=True)[:5]


def all_users(path=PATH):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        cur.execute('SELECT num_downloads, num_added, user_id FROM users')
        res = cur.fetchall()

        return sorted(res, reverse=True, key=key4users)[:5]


def key4users(a):
    return a[0] + a[1]
