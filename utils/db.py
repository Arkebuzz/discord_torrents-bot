import sqlite3

from config import PATH_DB as PATH


class DB:
    def __init__(self, path=PATH):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute('PRAGMA foreign_keys = ON;')
        self.cur = self.conn.cursor()

        self.create_db()

    def create_db(self):
        """
        Создаёт БД по пути path.

        :return:
        """

        self.cur.execute('''CREATE TABLE IF NOT EXISTS guilds(
               id INTEGER PRIMARY KEY,
               channel_id INTEGER);
               ''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY,
               added INTEGER,
               downloads INTEGER,
               votes INTEGER);
               ''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS games(
               name TEXT PRIMARY KEY,
               downloads INTEGER,
               score FLOAT);
               ''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS versions(
               id INTEGER PRIMARY KEY, 
               game_name INTEGER,
               version TEXT,
               user_id INTEGER,
               img_url TEXT,
               sys_requirements TEXT,
               description TEXT,
               FOREIGN KEY(game_name) REFERENCES games(name) ON DELETE CASCADE,
               FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
               ''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS genre4version(
               version_id INTEGER,
               genre INTEGER, 
               type INTEGER,
               FOREIGN KEY(version_id) REFERENCES versions(id) ON DELETE CASCADE);
               ''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS comments(
               user_id INTEGER, 
               game_name TEXT,
               score INTEGER,
               message TEXT,
               PRIMARY KEY(user_id, game_name),
               FOREIGN KEY(game_name) REFERENCES games(name) ON DELETE CASCADE,
               FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
               ''')

    def update_guild_settings(self, guild_id, channel_id):
        """
        Обновляет настройки канала сервера.

        :param guild_id: ID сервера.
        :param channel_id: Новое ID канала.
        :return:
        """

        self.cur.execute('INSERT INTO guilds VALUES(?, ?) ON CONFLICT (id) DO UPDATE SET channel_id = ?',
                         (guild_id, channel_id, channel_id))

        self.conn.commit()

    def get_guilds(self, guild_id=None):
        """
        Возвращает сервера бота c введенным ID, если ID не передан, то возвращает все сервера.

        :param guild_id: ID сервера.
        :return:
        """

        if guild_id is None:
            self.cur.execute('SELECT * FROM guilds;')
        else:
            self.cur.execute('SELECT * FROM guilds WHERE id = ?;', (guild_id,))

        res = self.cur.fetchall()

        return res

    def delete_guild(self, guild_id):
        """
        Удаление сервер из БД.

        :param guild_id: ID сервера.
        :return:
        """

        self.cur.execute('DELETE FROM guilds WHERE id = ?;', (guild_id,))
        self.conn.commit()

    def new_game(self, game):
        """
        Добавляет новую игру в БД.

        :param game: list[name, user_id, img, version, list[genre], list[gtype], sys, description]
        :return:
        """

        with sqlite3.connect(self.path) as conn:
            conn.execute('PRAGMA foreign_keys = ON;')
            cur = conn.cursor()

            cur.execute('INSERT INTO users VALUES(?, 1, 0, 0) ON CONFLICT (id) DO UPDATE SET added = added + 1',
                        (game[1],))

            cur.execute('INSERT INTO games VALUES(?, 0, 0.0) ON CONFLICT (name) DO NOTHING', (game[0],))

            cur.execute('INSERT INTO versions VALUES(NULL, ?, ?, ?, ?, ?, ?)',
                        (game[0], game[3], game[1], game[2], *game[6:]))

            lastrowid = cur.lastrowid

            cur.executemany('INSERT INTO genre4version VALUES(?, ?, ?)',
                            [(lastrowid, genre, None) for genre in game[4]] +
                            [(lastrowid, None, gtype) for gtype in game[5]])

            conn.commit()

        return lastrowid

    def check_game(self, name):
        """
        Проверяет есть ли игра в БД.

        :param name:
        :return:
        """

        self.cur.execute('SELECT * FROM games WHERE name = ?', (name,))
        return self.cur.fetchall()

    def search_games(self, name=None, genre=None, gtype=None):
        """
        Поиск игр по названию, типу или жанру, если параметры не переданы, выводит все игры.

        :param name: Название игры.
        :param genre: Жанры игры.
        :param gtype: Типы игры.
        :return: name, id, user_id, img_url, version, genre, type, sys_requirements, description, downloads, score
        """

        if name is not None:
            self.cur.execute(f'''
                SELECT game_name, id, user_id, img_url, max(version),  
                group_concat(genre.genre), group_concat(genre.type),
                sys_requirements, description, downloads, score 
                FROM games, versions
                JOIN genre4version AS genre ON genre.version_id = id
                WHERE name LIKE "%{name}%" AND game_name = name 
                GROUP BY name;
            ''')
            res = self.cur.fetchall()

        elif genre is not None and gtype is not None:
            genre_str = '", "'.join(map(str, genre))
            gtype_str = '", "'.join(map(str, gtype))

            self.cur.execute(f'''
                SELECT game_name, id, user_id, img_url, max(version),  
                group_concat(genre.genre), group_concat(genre.type),
                sys_requirements, description, downloads, score 
                FROM games, (
                         SELECT *
                         FROM genre4version, versions
                         WHERE id = version_id
                         AND ((genre IN ("{genre_str}")) OR (type IN ("{gtype_str}")))
                         GROUP BY id
                         HAVING COUNT(id) = ?
                     )
                JOIN genre4version AS genre ON genre.version_id = id
                WHERE game_name = name 
                GROUP BY name;
            ''', (len(genre) + len(gtype),))
            res = self.cur.fetchall()

        elif gtype is not None:
            gtype_str = '", "'.join(map(str, gtype))
            self.cur.execute(f'''
                SELECT game_name, id, user_id, img_url, max(version),  
                group_concat(genre.genre), group_concat(genre.type),
                sys_requirements, description, downloads, score 
                FROM games, (
                         SELECT *
                         FROM genre4version, versions
                         WHERE id = version_id
                         AND (type IN ("{gtype_str}"))
                         GROUP BY id
                         HAVING COUNT(id) = ?
                     )
                JOIN genre4version AS genre ON genre.version_id = id
                WHERE game_name = name 
                GROUP BY name;
            ''', (len(gtype),))
            res = self.cur.fetchall()

        elif genre is not None:
            genre_str = '", "'.join(map(str, genre))
            self.cur.execute(f'''
                SELECT game_name, id, user_id, img_url, max(version),  
                group_concat(genre.genre), group_concat(genre.type),
                sys_requirements, description, downloads, score 
                FROM games, (
                         SELECT *
                         FROM genre4version, versions
                         WHERE id = version_id
                         AND (genre IN ("{genre_str}"))
                         GROUP BY id
                         HAVING COUNT(id) = ?
                     )
                JOIN genre4version AS genre ON genre.version_id = id
                WHERE game_name = name 
                GROUP BY name;
            ''', (len(genre),))
            res = self.cur.fetchall()

        else:
            self.cur.execute('''
                SELECT game_name, id, user_id, img_url, max(version),  
                group_concat(genre.genre), group_concat(genre.type),
                sys_requirements, description, downloads, score 
                FROM games, versions
                JOIN genre4version AS genre ON genre.version_id = id
                WHERE game_name = name 
                GROUP BY id;
            ''')
            res = self.cur.fetchall()

        return res

    def get_version2delete(self, name=None, version=None, user=None):
        """
        Краткий поиск версий в БД. Должен быть передан только 1 параметр!

        :param name:
        :param version:
        :param user:
        :return:
        """

        if name is not None:
            self.cur.execute(f'''
                SELECT game_name, version, user_id 
                FROM versions
                WHERE game_name LIKE "%{name}%"
                GROUP BY game_name
                ''')
        elif version is not None:
            self.cur.execute(f'''
                SELECT game_name, version, user_id 
                FROM versions
                WHERE version LIKE "%{version}%"
                GROUP BY version
                ''')
        else:
            self.cur.execute(f'''
                SELECT game_name, version, user_id 
                FROM versions
                WHERE user_id LIKE "%{user}%"
                GROUP BY user_id
                ''')

        return self.cur.fetchall()

    def get_versions(self, game):
        if game:
            self.cur.execute('''
                SELECT game_name, id, user_id, img_url, version,  
                group_concat(genre.genre), group_concat(genre.type),
                sys_requirements, description
                FROM versions
                JOIN genre4version AS genre ON genre.version_id = id
                WHERE game_name = ?
                ''', (game,))
        else:
            self.cur.execute('''
                SELECT game_name, id, user_id, img_url, version,  
                group_concat(genre.genre), group_concat(genre.type),
                sys_requirements, description
                FROM versions
                JOIN genre4version AS genre ON genre.version_id = id
            ''')
        return self.cur.fetchall()

    def get_comments(self, game):
        self.cur.execute('SELECT user_id, score, message FROM comments WHERE game_name = ?', (game,))
        return self.cur.fetchall()

    def new_download(self, game_n, user_id):
        """
        Обновляет данные о количестве загрузок игры и пользователя.

        :param game_n: Название игры.
        :param user_id: ID пользователя.
        :return:
        """

        self.cur.execute(
            'INSERT INTO users VALUES(?, 0, 1, 0) ON CONFLICT (id) DO UPDATE SET downloads = downloads + 1',
            (user_id,)
        )

        self.cur.execute('UPDATE games SET downloads = downloads + 1 WHERE name = ?;', (game_n,))

        self.conn.commit()

    def new_reaction(self, name, user_id, react):
        """
        Добавление отзыва к игре.

        :param name: Название игры.
        :param user_id: ID пользователя.
        :param react: Отзыв (score, message).
        :return:
        """

        self.cur.execute('INSERT INTO users VALUES(?, 0, 0, 0) ON CONFLICT (id) DO NOTHING', (user_id,))

        try:
            self.cur.execute(
                'INSERT INTO comments VALUES(?, ?, ?, ?)',
                (user_id, name, *react)
            )
            self.cur.execute('UPDATE users SET votes = votes + 1 WHERE id = ?', (user_id,))

        except sqlite3.Error:
            self.cur.execute(
                'UPDATE comments SET score = ?, message = ? WHERE user_id = ? AND game_name=?',
                (*react, user_id, name)
            )

        self.conn.commit()
        self._update_game_score(name)

    def _update_game_score(self, game):
        """
        Пересчёт рейтинга игры по отзывам.

        :param game:
        :return:
        """
        self.cur.execute('''
            UPDATE games
            SET score = (SELECT avg(score) FROM comments WHERE game_name = name)
            WHERE name = ?;
        ''', (game,))

        self.conn.commit()

    def delete_version(self, name, version, user_id):
        self.cur.execute('DELETE FROM versions '
                         'WHERE game_name = ? AND version = ? AND user_id = ?',
                         (name, version, user_id))

        self.cur.execute('SELECT * FROM versions WHERE game_name = ?', (name,))
        if not self.cur.fetchall():
            self.cur.execute('DELETE FROM games WHERE name = ?', (name,))

    def top_games(self):
        """
        Возвращает все игры, отсортированные в порядке убывания скачиваний и комментариев.

        :return:
        """

        self.cur.execute('''
            SELECT name, downloads, score 
            FROM games
            ORDER BY score + downloads + score * downloads DESC;
        ''')
        return self.cur.fetchall()

    def top_users(self):
        """
        Возвращает всех пользователей в порядке убывания активности с ботом.

        :return:
        """

        self.cur.execute('''
            SELECT * 
            FROM users
            ORDER BY added * 5 + votes * 3 + downloads DESC;
        ''')
        return self.cur.fetchall()
