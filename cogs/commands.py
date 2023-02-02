import asyncio
import random

import disnake
from disnake.ext import commands

from cogs.modals import GameModal, VoteModal
from cogs.select_menu import SelectGameType, SelectGameGenre
from cogs.buttons import GameList, CommentsList
from utils.db import *
from utils.logger import logger
from utils.search_game_info import search_requirements, search_images


class OtherCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name='option',
        description='Выбрать основной канал для бота.'
    )
    async def option(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        update_guild_settings(inter.guild_id, channel.id)

        await inter.response.send_message('Выполнена настройка основного канала для бота, '
                                          f'теперь основной канал - {channel}')

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

        logger.info(f'[CALL] <@{inter.author.id}> /info')

        emb = disnake.Embed(title='Информация о боте:', color=disnake.Colour.blue())
        emb.set_thumbnail(r'https://www.pinclipart.com/picdir/big/525-5256722_file-circle-icons-gamecontroller-game'
                          r'-icon-png-circle.png')
        emb.add_field(name='Название:', value='GTBot')
        emb.add_field(name='Версия:', value='beta v0.8.1')
        emb.add_field(name='Описание:', value='Бот создан для упрощения обмена торрентами.', inline=False)
        emb.add_field(name='Что нового:',
                      value='```diff\nv0.8.1\n'
                            '+Изменён способ оценки игр: теперь это происходит во всплывающем окне.\n'
                            '+Реализована возможность добавления и просмотра комментариев к играм.\n'
                            '~Поиск игр разделён на 2 независимые команды:\n'
                            '    search_game4name - поиск игр по названию;\n'
                            '    search_game4type - поиск игр по жанровой принадлежности.\n'
                            '~Исправлены ошибки в автопоиске системных требований и фото к играм.'
                            '```', inline=False)
        emb.set_footer(text='@Arkebuzz#7717    https://github.com/Arkebuzz/ds_bot',
                       icon_url='https://sun1-27.userapi.com/s/v1/ig1'
                                '/FEUHI48F0M7K3DXhPtF_hChVzAsFiKAvaTvSG3966WmikzGIrLrj0u7UPX7o_zQ1vMW0x4CP.jpg?size'
                                '=400x400&quality=96&crop=528,397,709,709&ava=1')

        await inter.response.send_message(embed=emb)

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
            logger.warning(f'[FINISHED] <@{inter.author.id}> /new_game : file isn`t torrent')
            return

        file_name = ''
        for i in name:
            if i not in r'*."/\[]:;|,':
                file_name += i

        game = check_game(name, file_name)
        if game:
            emb = disnake.Embed(
                title='Данная игра уже есть в БД!',
                description=f'Найдите эту игру командой "/search {game[0][2]}"',
                color=disnake.Colour.red()
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
            logger.warning(f'[FINISHED] <@{inter.author.id}> /new_game : game already in DB')
            return

        req = await search_requirements(name)
        if not req:
            req = 'Не удалось найти системные требования для вашей игры.'
            logger.warning(f'[IN PROGRESS] <@{inter.author.id}> /new_game : system requirements not found')
            md = GameModal(name, placeholder_sr=req)
        else:
            md = GameModal(name, system_req=req)

        await inter.response.send_modal(modal=md)
        await md.wait()

        if md.res is None:
            logger.warning(f'[FINISHED] <@{inter.author.id}> /new_game : time is up for modal window')
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
            logger.warning(f'[FINISHED] <@{inter.author.id}> /new_game : game type not selected, time is up')
            return

        type_g = ', '.join(view.value)

        view = SelectGameGenre()
        await inter.edit_original_response(view=view)
        await view.wait()

        if view.value is None:
            logger.warning(f'[FINISHED] <@{inter.author.id}> /new_game : game genre not selected, time is up')
            return

        genre_g = ', '.join(view.value)

        await inter.edit_original_response('Игра в процессе добавления, ожидайте ...', view=None)

        os.mkdir(f'media/torrents/{file_name}')

        await search_images(name, file_name)

        emb = disnake.Embed(title='Добавлена новая игра!', color=disnake.Colour.blue())
        emb.add_field(name='Название:', value=name)
        emb.add_field(name='Версия:', value=version)
        emb.add_field(name='Тип игры:', value=type_g, inline=False)
        emb.add_field(name='Жанр игры:', value=genre_g, inline=False)
        emb.add_field(name='Системные требования:', value=req, inline=False)
        emb.add_field(name='Описание:', value=des, inline=False)
        emb.add_field(name='Автор добавления:', value=inter.author.mention, inline=False)
        emb.set_footer(text='Оцените игру при помощи кнопки под этим сообщением.')

        url = ''
        for channel in get_guilds():
            ch = self.bot.get_channel(channel[1])

            mes = await ch.send(
                embed=emb,
                file=disnake.File(f'media/torrents/{file_name}/' + os.listdir(f'media/torrents/{file_name}')[0]),
            )
            url = mes.attachments[0].url

        await torrent.save(f'media/torrents/{file_name}/' + file_name + '.torrent')

        new_game(name, url, inter.author.id, file_name, version, genre_g, type_g, req, des)

        if fix is not None:
            await fix.save(f'media/torrents/{file_name}/' + fix.filename)

        await inter.delete_original_response()

        logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : game is added {name}, {genre_g}, {type_g}')


class GameSearchCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def main_search(inter, name, gtype, genre):
        games = search_game(name, genre, gtype)
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
            comments = json.loads(games[i][10])
            sc = [int(c[0]) for c in comments.values()]
            score = sum(sc) / len(sc) if sc else 0

            emb = disnake.Embed(title=games[i][0], color=disnake.Colour.blue())
            emb.add_field(name='Версия:', value=games[i][4])
            emb.add_field(name='Количество скачиваний:', value=games[i][9])
            emb.add_field(name='Оценка:', value=score)
            emb.add_field(name='Тип игры:', value=games[i][6], inline=False)
            emb.add_field(name='Жанр игры:', value=games[i][5], inline=False)
            emb.add_field(name='Системные требования:', value=games[i][7], inline=False)
            emb.add_field(name='Описание:', value=games[i][8], inline=False)
            emb.add_field(name='Автор добавления:', value='<@' + str(games[i][2]) + '>', inline=False)
            emb.set_image(games[i][1])
            emb.set_footer(text=f'Страница {i + 1}/{ln}')

            view = GameList(ln, i)
            await inter.edit_original_response(content='', embed=emb, view=view)
            await view.wait()
            i = view.value

            if view.res is not None:
                temp_inter = view.inter
                f = view.res

                if f == 'd':
                    await temp_inter.response.send_message('Загрузка ...', ephemeral=True)

                    fls = []
                    for file in os.listdir(f'media/torrents/{games[i][3]}'):
                        if 'img.' not in file:
                            fls.append(disnake.File(f'media/torrents/{games[i][3]}/' + file))

                    await temp_inter.edit_original_response(f'{games[i][0]}, файлы:', files=fls)
                    new_download(games[i][0], inter.author.id)

                    games = search_game(name, genre, gtype)
                    ln = len(games)

                    logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search : game {games[i][0]} is downloaded')

                elif f == 'c':
                    await temp_inter.response.defer()

                    com = [[('', f'<@{user_id}> Оценка: {comments[user_id][0]}\n' + comments[user_id][1])
                            for user_id in list(comments)[ind:ind + 5]] for ind in range(0, len(comments), 5)]

                    j = 0
                    res = None
                    while j is not None and res is None:
                        emb = disnake.Embed(title=f'Отзывы о {games[i][0]}', color=disnake.Colour.blue())
                        emb.set_footer(text=f'Страница {j + 1}/{len(com)}')

                        for c in range(len(com[j])):
                            emb.add_field(com[j][c][0], com[j][c][1])

                        view = CommentsList(len(com), j)
                        await temp_inter.edit_original_response(embed=emb, view=view)
                        await view.wait()
                        j = view.value
                        res = view.res

                    logger.info(f'[IN PROGRESS] <@{inter.author.id}> /search : game {games[i][0]} CALL comments')
                    continue

                elif f == 'v':
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
                        continue

                    res = md.res
                    score = res[0][1]
                    comment = res[1][1]

                    temp_inter = md.inter

                    if score in '12345':
                        add_reaction(games[i][0], inter.author.id, [score, comment])
                        await temp_inter.edit_original_response('Ваш отзыв добавлен!', )
                        logger.info(f'[NEW REACT] <@{inter.author.id}> game: {games[i][0]}; score: {score}')

                        games = search_game(name, genre, gtype)
                        ln = len(games)
                    else:
                        await temp_inter.edit_original_response(
                            'Невозможно сохранить Ваш отзыв, неверный формат ввода!'
                        )

        else:
            await inter.delete_original_response()
            logger.warning(f'[FINISHED] <@{inter.author.id}> /search : time`s up')

    @commands.slash_command(
        name='search_game4type',
        description='Ищет игру по жанровой принадлежности.'
    )
    async def search_type(self, inter: disnake.ApplicationCommandInteraction,
                          stype: str = commands.Param(choices=['Поиск по жанру', 'Поиск по типу']), ):
        """
        Поиск игр по жанровой принадлежности.

        :param inter:
        :param stype:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /search_type stype: {stype}')

        await inter.response.defer(ephemeral=True)

        if stype == 'Поиск по жанру':
            view = SelectGameGenre()
            await inter.edit_original_response(view=view)
            await view.wait()
            genre = view.value

            if genre is None:
                await inter.delete_original_response()
                return

            gtype = None
            name = None

        else:
            view = SelectGameType()
            await inter.edit_original_response(view=view)
            await view.wait()
            gtype = view.value

            if gtype is None:
                await inter.delete_original_response()
                return

            genre = None
            name = None

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
        return [name[0] for name in search_game(string)]


class Statistic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='game_top',
        description='Топ игр по количеству скачиваний.',
    )
    async def game_top(self, inter: disnake.ApplicationCommandInteraction):
        """
        Слэш-команда, выводит топ игр по количеству скачиваний.
        :param inter:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /game_top')

        games = top_games()

        emb = disnake.Embed(title='Топ игр', color=disnake.Colour.blue())
        emb.add_field(name='Игра', value='\n'.join([i[2] for i in games]))
        emb.add_field(name='Рейтинг', value='\n'.join([str(i[0]) for i in games]))
        emb.add_field(name='Загрузки', value='\n'.join([str(i[1]) for i in games]))

        await inter.response.send_message(embed=emb)

    @commands.slash_command(
        name='user_top',
        description='Топ пользователей по количеству активности.',
    )
    async def user_top(self, inter: disnake.ApplicationCommandInteraction):
        """
        Слэш-команда, выводит топ пользователей по активности.
        :param inter:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /user_top')

        users = top_users()

        emb = disnake.Embed(title='Топ пользователей', color=disnake.Colour.blue())
        emb.add_field(name='Ник', value='\n'.join(['<@' + str(i[0]) + '>' for i in users]))
        emb.add_field(name='Скачиваний/Добавлений', value='\n'.join([str(i[2]) + ' / ' + str(i[1]) for i in users]))
        emb.add_field(name='Отзывов', value='\n'.join([str(i[3]) for i in users]))

        await inter.response.send_message(embed=emb)


def setup(bot: commands.Bot):
    bot.add_cog(OtherCommand(bot))
    bot.add_cog(GameSearchCommand(bot))
    bot.add_cog(GameNewCommand(bot))
    bot.add_cog(Statistic(bot))
