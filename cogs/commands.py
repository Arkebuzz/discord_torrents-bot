import random
import shutil
import os

from disnake.ext import commands

from cogs.modals import GameModal, VoteModal
from cogs.select_menu import SelectGameType, SelectGameGenre
from cogs.buttons import *
from config import ADMINS, GENRE_OPTIONS, TYPE_OPTIONS
from utils.db import DB
from utils.logger import logger
from utils.search_game_info import search_requirements, search_images

db = DB()


class OtherCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name='set_main_channel',
        description='Выбрать основной канал для бота.'
    )
    async def settings(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        """
        Слэш-команда, производит настройку канала для бота на сервере.

        :param inter:
        :param channel:
        :return:
        """

        db.update_guild_settings(inter.guild_id, channel.id)

        await inter.response.send_message('Выполнена настройка основного канала для бота, '
                                          f'теперь основной канал - {channel}')

        logger.info(f'[CALL] <@{inter.author.id}> set_main_channel channel: {channel}')

    @commands.slash_command(
        name='delete_game',
        description='Удалить версию игры'
    )
    async def delete_game(self, inter: disnake.ApplicationCommandInteraction,
                          name: str, version: str, user_id: str):
        """
        Слэш-команда, позволяет админу удалить версию игры.

        :param inter:
        :param name:
        :param version:
        :param user_id:
        :return:
        """

        if inter.author.id in ADMINS:
            db.delete_version(name, version, user_id)
            await inter.response.send_message('Все версии игр с заданными данными удалены!', ephemeral=True)
            logger.info(f'[CALL] <@{inter.author.id}> /delete_game name: {name}, version: {version} GAME`s DELETE')
        else:
            await inter.response.send_message('У вас нет прав для выполнения данной операции!', ephemeral=True)
            logger.info(f'[CALL] <@{inter.author.id}> /delete_game name: {name}, version: {version} NO RIGHTS')

    @delete_game.autocomplete('name')
    async def autocomplete(self, _, string: str):
        return [name[0] for name in db.get_version2delete(name=string)[:25]]

    @delete_game.autocomplete('version')
    async def autocomplete(self, _, string: str):
        return [name[1] for name in db.get_version2delete(version=string)[:25]]

    @delete_game.autocomplete('user_id')
    async def autocomplete(self, _, string: str):
        return [str(name[2]) for name in db.get_version2delete(user=string)[:25]]

    @commands.slash_command(
        name='info',
        description='Информация о боте.',
    )
    async def info(self, inter: disnake.ApplicationCommandInteraction):
        """
        Слэш-команда, отправляет в ответ информацию о боте.

        :param inter:
        :return:
        """

        emb = disnake.Embed(title='Информация о боте:', color=disnake.Colour.blue())
        emb.set_thumbnail(r'https://www.pinclipart.com/picdir/big/525-5256722_file-circle-icons-gamecontroller-game'
                          r'-icon-png-circle.png')
        emb.add_field(name='Название:', value='GTBot')
        emb.add_field(name='Версия:', value='release v1.2')
        emb.add_field(name='Описание:', value='Бот создан для упрощения обмена торрентами.', inline=False)
        emb.add_field(name='Что нового:',
                      value='```diff\nv1\n'
                            '+Оптимизирован просмотр версий игр.\n'
                            '+Добавлена возможность удалять игры.\n'
                            '~Изменён поиск по жанровой принадлежности.\n'
                            '~Проведены оптимизация кода и исправление ошибок.'
                            '```', inline=False)
        emb.set_footer(text='@Arkebuzz#7717\nhttps://github.com/Arkebuzz/ds_bot',
                       icon_url='https://sun1-27.userapi.com/s/v1/ig1'
                                '/FEUHI48F0M7K3DXhPtF_hChVzAsFiKAvaTvSG3966WmikzGIrLrj0u7UPX7o_zQ1vMW0x4CP.jpg?size'
                                '=400x400&quality=96&crop=528,397,709,709&ava=1')

        await inter.response.send_message(embed=emb)
        logger.info(f'[CALL] <@{inter.author.id}> /info')

    @commands.slash_command(
        name='ping',
        description='Узнать задержку бота.',
    )
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """
        Слэш-команда, отправляет в ответ пинг.

        :param inter:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /ping')

        await inter.response.send_message(f'Пинг: {round(self.bot.latency * 1000)}мс', ephemeral=True)

    @commands.slash_command(
        name='roll',
        description='Случайное число от 1 до 100.',
    )
    async def roll(self, inter: disnake.ApplicationCommandInteraction):
        """
        Слэш-команда, отправляет в ответ число от 1 до 100.

        :param inter:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /roll')

        await inter.response.send_message(random.randint(1, 100))


class GameNewCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name='new_game',
        description='Добавить новую игру. Введите название игры.',
    )
    async def new_game(self, inter: disnake.ApplicationCommandInteraction, name: str,
                       torrent: disnake.Attachment, fix: disnake.Attachment = None):
        """
        Слэш-команда, добавляет новую игры в библиотеку.

        :param inter:
        :param name:
        :param torrent:
        :param fix:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /new_game name: {name}; torrent: {torrent.filename}; '
                    f'fix: {fix.filename if fix is not None else None}')

        if torrent.content_type != 'application/x-bittorrent':
            emb = disnake.Embed(
                title='Прикрепленный файл не является торрент-файлом!',
                description=f'{torrent.filename} - {torrent.content_type} файл.',
                color=disnake.Colour.red()
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
            logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : file isn`t torrent')
            return

        file_name = ''
        for i in name:
            if i not in r'*."/\[]:;|,':
                file_name += i

        game = db.check_game(name)
        if game:
            logger.info(f'[IN PROGRESS] <@{inter.author.id}> /new_game : game already in DB')

            emb = disnake.Embed(
                title='Данная игра уже есть в БД!',
                description='Найдите эту игру, нажав "Перейти к поиску", или нажмите кнопку "Добавить игру", '
                            'чтобы добавить новую версию этой игры.',
                color=disnake.Colour.red()
            )
            view = Confirm()
            await inter.response.send_message(embed=emb, view=view, ephemeral=True)

            await view.wait()
            f = view.res
            inter = view.inter

            if f == 'search':
                logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : starting search')
                await inter.response.defer()
                await GameSearchCommand(self.bot).main_search(inter, name, None, None)
                return

            elif f is None:
                await inter.delete_original_response()
                logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : no response to confirmation, time is up')
                return

            logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : confirm, continue')

        req = await search_requirements(name)
        if not req:
            req = 'Не удалось найти системные требования для вашей игры.'
            logger.warning(f'[IN PROGRESS] <@{inter.author.id}> /new_game : system requirements not found name: {name}')
            md = GameModal(name, placeholder_sr=req)
        else:
            md = GameModal(name, system_req=req)

        await inter.response.send_modal(modal=md)
        await md.wait()

        if md.res is None:
            logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : time is up for modal window')
            return

        name = md.res[0][1]
        version = md.res[1][1]
        req = md.res[2][1]
        des = md.res[3][1]
        inter = md.inter

        view = SelectGameType()
        await inter.edit_original_response(view=view)
        await view.wait()

        if view.value is None:
            logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : game type not selected, time is up')
            return

        gtype = view.value
        type_str = ', '.join([TYPE_OPTIONS[ind - 100][0] for ind in view.value])

        view = SelectGameGenre()
        await inter.edit_original_response(view=view)
        await view.wait()

        if view.value is None:
            logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : game genre not selected, time is up')
            return

        genre = view.value
        genre_str = ', '.join([GENRE_OPTIONS[ind] for ind in view.value])

        await inter.edit_original_response('Игра в процессе добавления, ожидайте ...', view=None)

        emb = disnake.Embed(title='Добавлена новая игра!', color=disnake.Colour.blue())
        emb.add_field(name='Название:', value=name)
        emb.add_field(name='Версия:', value=version)
        emb.add_field(name='Тип игры:', value=type_str, inline=False)
        emb.add_field(name='Жанр игры:', value=genre_str, inline=False)
        emb.add_field(name='Системные требования:', value=req, inline=False)
        emb.add_field(name='Описание:', value=des, inline=False)
        emb.add_field(name='Автор добавления:', value=inter.author.mention, inline=False)

        file = await search_images(name, inter.author.id)

        if db.get_guilds() and file is not None:
            for channel in db.get_guilds():
                ch = self.bot.get_channel(channel[1])
                mes = await ch.send(
                    embed=emb,
                    file=disnake.File(file),
                )

            url = mes.attachments[0].url

        else:
            for channel in db.get_guilds():
                ch = self.bot.get_channel(channel[1])
                await ch.send(embed=emb)

            url = ''

        path = db.new_game((name, inter.author.id, url, version, genre, gtype, req, des))

        if os.path.isdir(f'media/torrents/{path}'):
            shutil.rmtree(f'media/torrents/{path}')
        os.makedirs(f'media/torrents/{path}')

        await torrent.save(f'media/torrents/{path}/' + file_name + '.torrent')

        if fix is not None:
            await fix.save(f'media/torrents/{path}/' + fix.filename)

        await inter.delete_original_response()

        logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : game is added {name}, {genre_str}, {type_str}')


class GameSearchCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def main_search(inter, name, gtype, genre):
        games = db.search_games(name, genre, gtype)
        ln = len(games)

        if not ln:
            emb = disnake.Embed(
                title='Данной игры нет в БД!',
                description='Игр c данными тегами нет в базе данных бота. '
                            'Вы можете добавить новые игры при помощи команды "/new_game"',
                color=disnake.Colour.red()
            )

            await inter.edit_original_response(embed=emb, view=None)
            logger.warning(f'[FINISHED] <@{inter.author.id}> /search : games not found')
            return

        i = 0
        while i is not None:
            gtype = ', '.join([TYPE_OPTIONS[int(ind) - 100][0] for ind in games[i][6].split(',')])
            genre = ', '.join([GENRE_OPTIONS[int(ind)] for ind in games[i][5].split(',')])

            emb = disnake.Embed(title=games[i][0], color=disnake.Colour.blue())
            emb.add_field(name='Версия:', value=games[i][4])
            emb.add_field(name='Загрузки:', value=games[i][9])
            emb.add_field(name='Оценка:', value=round(games[i][10], 2))
            emb.add_field(name='Тип игры:', value=gtype, inline=False)
            emb.add_field(name='Жанр игры:', value=genre, inline=False)
            emb.add_field(name='Системные требования:', value=games[i][7], inline=False)
            emb.add_field(name='Описание:', value=games[i][8], inline=False)
            emb.add_field(name='Автор добавления:', value='<@' + str(games[i][2]) + '>', inline=False)
            emb.set_image(games[i][3])
            emb.set_footer(text=f'Страница {i + 1}/{ln}\n')

            view = GameList(ln, i)
            await inter.edit_original_response(content='', embed=emb, view=view)
            await view.wait()
            i = view.value

            if view.res is not None:
                temp_inter = view.inter
                f = view.res

                if f == 'versions':
                    await temp_inter.response.defer()
                    logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search : game {games[i][0]} CALL versions')

                    vers = db.get_versions(games[i][0])

                    j = 0
                    res = None
                    while j is not None and res != 'back':
                        temp_gtype = ', '.join([TYPE_OPTIONS[int(ind) - 100][0] for ind in vers[j][6].split(',')])
                        temp_genre = ', '.join([GENRE_OPTIONS[int(ind)] for ind in vers[j][5].split(',')])

                        emb = disnake.Embed(title=f'Скачать {games[i][0]}', color=disnake.Colour.blue())
                        emb.add_field(name='Версия:', value=vers[j][4])
                        emb.add_field(name='Тип игры:', value=temp_gtype, inline=False)
                        emb.add_field(name='Жанр игры:', value=temp_genre, inline=False)
                        emb.add_field(name='Описание:', value=vers[j][8], inline=False)
                        emb.add_field(name='Автор добавления:', value='<@' + str(vers[j][2]) + '>', inline=False)
                        emb.set_footer(text=f'Страница {j + 1}/{len(vers)}\n')

                        view = FlippingBackDownload(len(vers), j)
                        await temp_inter.edit_original_response(content=None, embed=emb, view=view)
                        await view.wait()
                        j = view.value
                        res = view.res

                        if res == 'download':
                            fls = []
                            for f in os.listdir(f'media/torrents/{vers[j][1]}/'):
                                fls.append(disnake.File(f'media/torrents/{vers[j][1]}/' + f))

                            await temp_inter.edit_original_response(view=None, files=fls)
                            db.new_download(vers[j][0], inter.author.id)

                            logger.info(
                                f'[FINISHED] <@{inter.author.id}> /search : game {games[i][0]} is downloaded'
                            )
                            return

                    logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search : game {games[i][0]} FINISHED download')
                    await temp_inter.edit_original_response(embed=emb, view=view, attachments=None)

                    continue

                elif f == 'comments':
                    await temp_inter.response.defer()
                    logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search : game {games[i][0]} CALL comments')

                    comments = db.get_comments(games[i][0])

                    if not comments:
                        view = Back()
                        await temp_inter.edit_original_response('У этой игры нет комментариев.', embed=None, view=view)
                        await view.wait()
                        res = view.res

                        if res is not None:
                            continue
                        else:
                            await temp_inter.delete_original_response()
                            logger.warning(f'[FINISHED] <@{inter.author.id}> /search : time`s up')
                            return

                    com = [[f'<@{comment[0]}> Оценка: {comment[1]}\n' + comment[2] for comment in comments[ind:ind + 5]]
                           for ind in range(0, len(comments), 5)]

                    j = 0
                    res = None
                    while j is not None and res is None:
                        emb = disnake.Embed(title=f'Отзывы о {games[i][0]}', color=disnake.Colour.blue())
                        emb.set_footer(text=f'Страница {j + 1}/{len(com)}')

                        for c in range(len(com[j])):
                            emb.add_field('', com[j][c], inline=False)

                        view = FlippingBack(len(com), j)
                        await temp_inter.edit_original_response(embed=emb, view=view)
                        await view.wait()
                        j = view.value
                        res = view.res

                    logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search : game {games[i][0]} FINISHED comments')
                    continue

                elif f == 'vote':
                    logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search : game {games[i][0]} CALL vote')

                    md = VoteModal()

                    await inter.edit_original_response(
                        'Оцените игру во всплывающем окне.\n'
                        'Если вы закрыли всплывающее окно и видите это сообщение, то удалите его.',
                        view=None, embed=None
                    )

                    await temp_inter.response.send_modal(md)
                    await md.wait()

                    if md.res is None:
                        await temp_inter.edit_original_response('Невозможно сохранить Ваш отзыв, время истекло!')
                        logger.info(f'[NEW REACT] <@{inter.author.id}> game: {games[i][0]} time`s up')
                        continue

                    res = md.res
                    score = res[0][1]
                    comment = res[1][1]

                    temp_inter = md.inter

                    if score in '12345':
                        db.new_reaction(games[i][0], inter.author.id, [score, comment])
                        await temp_inter.edit_original_response('Ваш отзыв добавлен!', )
                        logger.info(f'[NEW REACT] <@{inter.author.id}> game: {games[i][0]}; score: {score}')

                        games = db.search_games(name, genre, gtype)
                        ln = len(games)
                    else:
                        await temp_inter.edit_original_response(
                            'Невозможно сохранить Ваш отзыв, неверный формат ввода!'
                        )
                        logger.warning(f'[NEW REACT] <@{inter.author.id}> game: {games[i][0]}; '
                                       f'score: {score}, mes: {comment}')

        else:
            await inter.delete_original_response()
            logger.warning(f'[FINISHED] <@{inter.author.id}> /search : time`s up')

    @commands.slash_command(
        name='search_game4type',
        description='Ищет игру по жанровой принадлежности.'
    )
    async def search_type(self, inter: disnake.ApplicationCommandInteraction):
        """
        Поиск игр по жанровой принадлежности.

        :param inter:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /search_type')

        await inter.response.defer(ephemeral=True)

        name = None

        view = SelectGameType()
        await inter.edit_original_response(view=view)
        await view.wait()
        gtype = view.value

        if gtype is None:
            await inter.delete_original_response()
            return

        view = SelectGameGenre()
        await inter.edit_original_response(view=view)
        await view.wait()
        genre = view.value

        if genre is None:
            await inter.delete_original_response()
            return

        logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search_type starting main_search')

        await self.main_search(inter, name, gtype, genre)

    @commands.slash_command(
        name='search_game4name',
        description='Ищет игру по названию.'
    )
    async def search_name(self, inter: disnake.ApplicationCommandInteraction,
                          name: str):
        """
        Слэш-команда, ищет игру по названию.

        :param inter:
        :param name:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /search_name name: {name}')

        await inter.response.defer(ephemeral=True)

        logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search_name starting main_search')

        await self.main_search(inter, name, None, None)

    @search_name.autocomplete('name')
    async def autocomplete(self, _, string: str):
        return [name[0] for name in db.search_games(string)[:25]]


class Statistic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='top_games',
        description='Топ игр по количеству скачиваний.',
    )
    async def top_games(self, inter: disnake.ApplicationCommandInteraction):
        """
        Слэш-команда, выводит топ игр по количеству скачиваний.

        :param inter:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /game_top')

        games = db.top_games()[:10]

        emb = disnake.Embed(title='Топ игр', color=disnake.Colour.blue())
        emb.add_field(name='Игра', value='\n'.join([g[0] for g in games]))
        emb.add_field(name='Рейтинг', value='\n'.join([str(g[2])[:4] for g in games]))
        emb.add_field(name='Загрузки', value='\n'.join([str(g[1]) for g in games]))

        await inter.response.send_message(embed=emb)

    @commands.slash_command(
        name='top_users',
        description='Топ пользователей по количеству активности.',
    )
    async def top_users(self, inter: disnake.ApplicationCommandInteraction):
        """
        Слэш-команда, выводит топ пользователей по активности.

        :param inter:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /user_top')

        users = db.top_users()[:10]

        emb = disnake.Embed(title='Топ пользователей', color=disnake.Colour.blue())
        emb.add_field(name='Ник', value='\n'.join(['<@' + str(i[0]) + '>' for i in users]))
        emb.add_field(name='Скачиваний/Добавлений', value='\n'.join([str(i[2]) + ' / ' + str(i[1]) for i in users]))
        emb.add_field(name='Отзывов', value='\n'.join([str(i[3]) for i in users]))

        await inter.response.send_message(embed=emb)


def setup(bot: commands.Bot):
    """Регистрация команд бота."""

    bot.add_cog(OtherCommand(bot))
    bot.add_cog(GameSearchCommand(bot))
    bot.add_cog(GameNewCommand(bot))
    bot.add_cog(Statistic(bot))
