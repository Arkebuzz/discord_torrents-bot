import random

import disnake
from disnake.ext import commands

from cogs.modals import NewGameModal
from cogs.select_menu import SelectGameType, SelectGameGenre
from cogs.buttons import Flipping
from utils.db import *
from utils.logger import logger
from utils.search_game_requirements import search_requirements, search_images


class OtherCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name='option',
        description='Выбрать основной канал для бота.'
    )
    async def option(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        game_guild_settings(inter.guild_id, channel.id)

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
        emb.add_field(name='Версия:', value='beta v0.7.2')
        emb.add_field(name='Описание:', value='Бот создан для упрощения обмена торрентами.', inline=False)
        emb.add_field(name='Что нового:',
                      value='```diff\nv0.7.2\n'
                            '+Повышена плавность изменения сообщений при добавлении новых игр.'
                            '+Добавлен автоматический поиск фото к игре (работает вместе с автопоиском системных '
                            'требований, не найдены системные требования - не будет фото).'
                            '+Автообновление всех серверов при запуске бота.'
                            '~Исправлена ошибка неправильного подсчёта оценки игры и количества оценок пользователей.'
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


class GameCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name='search',
        description='Ищет игры по названию или жанрам. Выберите вариант поиска.'
    )
    async def search(self, inter: disnake.ApplicationCommandInteraction,
                     stype: str = commands.Param(choices=['Поиск по названию', 'Поиск по жанру', 'Поиск по типу']),
                     name: str = None):
        """
        Слэш-команда, ищет игры по названию или по жанровой принадлежности.

        :param inter:
        :param stype:
        :param name:
        :return:
        """

        logger.info(f'[CALL] <@{inter.author.id}> /search stype: {stype}; name: {name}')

        await inter.response.defer(ephemeral=True)

        if stype == 'Поиск по названию':
            if name is None:
                emb = disnake.Embed(
                    title='Поиск по данным параметрам невозможен!',
                    description='Вы выбрали поиск игр по названию и не передали параметр name.',
                    color=disnake.Colour.red()
                )
                await inter.response.send_message(embed=emb, ephemeral=True)

                logger.warning(f'[FINISHED] <@{inter.author.id}> /search : incorrect parameters')
                return

            genre = None
            gtype = None

        elif stype == 'Поиск по жанру':
            view = SelectGameGenre()
            await inter.edit_original_response(view=view)
            await view.wait()
            genre = view.value

            if genre is None:
                return

            gtype = None
            name = None

        else:
            view = SelectGameType()
            await inter.edit_original_response(view=view)
            await view.wait()
            gtype = view.value

            if gtype is None:
                return

            genre = None
            name = None

        res = search_game(name, genre, gtype)
        ln = len(res)

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
            if type(i) is str:
                if i[0] == 'd':

                    await inter.edit_original_response(embed=emb, view=None)
                    new_download(res[int(i[1:])][0], inter.author.id)
                    logger.info(f'[FINISHED] <@{inter.author.id}> /search : game {name} is downloaded')

                else:
                    mes_id = res[int(i[1:])][3].split()

                    for j in mes_id:
                        j = list(map(int, j.split('/')))
                        ch = self.bot.get_channel(j[0])
                        mes = int(j[1])

                        if inter.guild_id == ch.guild.id:
                            url = str(ch.guild.id) + '/' + str(ch.id) + '/' + str(mes)
                            break
                    else:
                        emb = disnake.Embed(title='Добавлена новая игра!', color=disnake.Colour.blue())
                        emb.add_field(name='Название:', value=res[int(i[1:])][0])
                        emb.add_field(name='Версия:', value=res[int(i[1:])][5])
                        emb.add_field(name='Тип игры:', value=res[int(i[1:])][7], inline=False)
                        emb.add_field(name='Жанр игры:', value=res[int(i[1:])][6], inline=False)
                        emb.add_field(name='Системные требования:', value=res[int(i[1:])][8], inline=False)
                        emb.add_field(name='Описание:', value=res[int(i[1:])][9], inline=False)
                        emb.add_field(name='Автор добавления:', value='<@' + str(res[int(i[1:])][2]) + '>',
                                      inline=False)
                        emb.set_image(res[int(i[1:])][1])
                        emb.set_footer(text='Оцените игру при помощи реакций под этим сообщением.')

                        mes = await inter.channel.send(embed=emb)
                        await mes.add_reaction('1️⃣')
                        await mes.add_reaction('2️⃣')
                        await mes.add_reaction('3️⃣')
                        await mes.add_reaction('4️⃣')
                        await mes.add_reaction('5️⃣')

                        url = str(mes.guild.id) + '/' + str(mes.channel.id) + '/' + str(mes.id)
                        game_guild_settings(res[int(i[1:])][0], res[int(i[1:])][2] + ' ' + url)

                    emb = disnake.Embed(title=res[int(i[1:])][0], color=disnake.Colour.blue(),
                                        description=f'https://discord.com/channels/' + url)
                    await inter.edit_original_response(embed=emb, view=None)
                break

            sc = json.loads(res[i][11])
            score = sum(sc.values()) / len(sc) if res[i][11] else 0

            emb = disnake.Embed(title=res[i][0], color=disnake.Colour.blue())
            emb.add_field(name='Версия:', value=res[i][5])
            emb.add_field(name='Количество скачиваний:', value=res[i][10])
            emb.add_field(name='Оценка:', value=score)
            emb.add_field(name='Тип игры:', value=res[i][7], inline=False)
            emb.add_field(name='Жанр игры:', value=res[i][6], inline=False)
            emb.add_field(name='Системные требования:', value=res[i][8], inline=False)
            emb.add_field(name='Описание:', value=res[i][9], inline=False)
            emb.add_field(name='Автор добавления:', value='<@' + str(res[i][2]) + '>', inline=False)
            emb.set_image(res[i][1])
            emb.set_footer(text=f'Страница {i + 1 if i >= 0 else ln + i + 1}/{ln}')

            view = Flipping(ln, i)
            await inter.edit_original_response(embed=emb, view=view)
            await view.wait()
            i = view.res

        else:
            await inter.delete_original_response()
            logger.warning(f'[FINISHED] <@{inter.author.id}> /search : time`s up')

    @search.autocomplete('name')
    async def option_autocomp(self, _, string: str):
        return [name[0] for name in search_game(string)]

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
            md = NewGameModal(name, placeholder_sr=req)
        else:
            md = NewGameModal(name, system_req=req)

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
        type_g = ', '.join(view.value)

        if type_g is None:
            logger.warning(f'[FINISHED] <@{inter.author.id}> /new_game : game type not selected, time is up')
            return

        view = SelectGameGenre()
        await inter.edit_original_response(view=view)
        await view.wait()
        genre_g = ', '.join(view.value)

        if genre_g is None:
            logger.warning(f'[FINISHED] <@{inter.author.id}> /new_game : game genre not selected, time is up')
            return

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
        emb.set_footer(text='Оцените игру при помощи реакций под этим сообщением.')

        mess = []
        url = ''
        for channel in get_guilds():
            ch = self.bot.get_channel(channel[1])

            mes = await ch.send(embed=emb, file=disnake.File(
                f'media/torrents/{file_name}/' + os.listdir(f'media/torrents/{file_name}')[0]))
            url = mes.attachments[0].url

            await mes.add_reaction('1️⃣')
            await mes.add_reaction('2️⃣')
            await mes.add_reaction('3️⃣')
            await mes.add_reaction('4️⃣')
            await mes.add_reaction('5️⃣')

            mess.append(str(ch.id) + '/' + str(mes.id))

        await torrent.save(f'media/torrents/{file_name}/' + file_name + '.torrent')

        mes_id = ' '.join(mess)
        new_game(name, url, inter.author.id, mes_id, file_name, version, genre_g, type_g, req, des)

        if fix is not None:
            await fix.save(f'media/torrents/{file_name}/' + fix.filename)

        await inter.delete_original_response()

        logger.info(f'[FINISHED] <@{inter.author.id}> /new_game : game is added {name}, {genre_g}, {type_g}')

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
        emb.add_field(name='Загрузки', value='\n'.join([str(i[0]) for i in games]))
        emb.add_field(name='Рейтинг', value='\n'.join([str(i[1]) for i in games]))

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
    bot.add_cog(GameCommand(bot))
