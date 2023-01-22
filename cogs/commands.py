import random
import os

import disnake
from disnake.ext import commands

from cogs.modals import NewGameModal
from cogs.select_menu import SelectGameType, SelectGameGenre
from cogs.buttons import Flipping
from utils.db import *
from utils.search_game_requirements import search_requirements


class OtherCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
        emb.add_field(name='Версия:', value='pre-alpha v0.3')
        emb.add_field(name='Описание:', value='Бот создан для упрощения обмена торрентами.', inline=False)
        emb.add_field(name='Что нового:',
                      value='```diff\nv0.3\n'
                            '+Добавлена статистика загрузок каждой игры.\n'
                            '+Добавлена статистика пользователей.\n'
                            '~Починен поиск по играм.\n'
                            '```', inline=False)
        emb.set_footer(text='@Arkebuzz#7717',
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

        await inter.response.send_message(random.randint(1, 100))


class GameCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name='search',
        description='Ищет игры по названию или жанрам. Выберете вариант поиска'
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

        await inter.response.defer(ephemeral=True)

        if stype == 'Поиск по названию':
            if name is None:
                emb = disnake.Embed(
                    title='Поиск по данным параметрам невозможен!',
                    description='Вы выбрали поиск игр по названию и не передали параметр name.',
                    color=disnake.Colour.red()
                )
                await inter.response.send_message(embed=emb, ephemeral=True)
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
                description=f'Игр c данными тегами нет в базе данных бота. '
                            'Вы можете добавить новые игры при помощи команды "/new_game"',
                color=disnake.Colour.red()
            )
            await inter.edit_original_response(embed=emb)
            return

        i = 0
        while i is not None:
            if type(i) is str:
                fls = []
                path = f'media/torrents/{res[int(i)][2]}/'

                for file in os.listdir(path):
                    fls.append(disnake.File(path + file))

                await inter.edit_original_response(embed=emb, files=fls, view=None)
                new_download(res[int(i)][0], res[int(i)][1])
                break

            name, author, _, version, genre_g, type_g, req, des, num_downloads = res[i]
            view = Flipping(ln, i)

            emb = disnake.Embed(title=name, color=disnake.Colour.blue())
            emb.add_field(name='Версия:', value=version)
            emb.add_field(name='Количество скачиваний:', value=num_downloads)
            emb.add_field(name='Тип игры:', value=type_g, inline=False)
            emb.add_field(name='Жанр игры:', value=genre_g, inline=False)
            emb.add_field(name='Системные требования:', value=req, inline=False)
            emb.add_field(name='Описание:', value=des, inline=False)
            emb.add_field(name='Автор добавления:', value='<@' + str(author) + '>', inline=False)
            emb.set_footer(text=f'Страница {i + 1 if i >= 0 else ln + i + 1}/{ln}')

            await inter.edit_original_response(embed=emb, view=view)
            await view.wait()
            i = view.res

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

        if torrent.content_type != 'application/x-bittorrent':
            emb = disnake.Embed(
                title='Прикрепленный файл не является торрент-файлом!',
                description=f'{torrent.filename} - {torrent.content_type} файл.',
                color=disnake.Colour.red()
            )
            await inter.response.send_message(embed=emb, ephemeral=True)
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
            return

        req = await search_requirements(name)
        if not req:
            req = ('Не удалось найти системные требования для вашей игры.\n'
                   'Если Вы уверены, что правильно написали название игры, '
                   'то введите системные требования самостоятельно.')

        md = NewGameModal(name, req)
        await inter.response.send_modal(modal=md)
        await md.wait()

        name = md.res[0][1]
        version = md.res[1][1]
        req = md.res[2][1]
        des = md.res[3][1]

        view = SelectGameType(followup=True)
        await inter.followup.send(view=view, ephemeral=True)
        await view.wait()
        type_g = ', '.join(view.value)

        if type_g is None:
            return

        view = SelectGameGenre(followup=True)
        await inter.followup.send(view=view, ephemeral=True)
        await view.wait()
        genre_g = ', '.join(view.value)

        if genre_g is None:
            return

        emb = disnake.Embed(title='Добавлена новая игра!', color=disnake.Colour.blue())
        emb.add_field(name='Название:', value=name)
        emb.add_field(name='Версия:', value=version)
        emb.add_field(name='Тип игры:', value=type_g, inline=False)
        emb.add_field(name='Жанр игры:', value=genre_g, inline=False)
        emb.add_field(name='Системные требования:', value=req, inline=False)
        emb.add_field(name='Описание:', value=des, inline=False)
        emb.add_field(name='Автор добавления:', value=inter.author.mention, inline=False)

        await inter.followup.send(embed=emb)

        if not os.path.isdir(f'media/torrents/{file_name}'):
            os.mkdir(f'media/torrents/{file_name}')
            await torrent.save(f'media/torrents/{file_name}/' + file_name + '.torrent')

            new_game(inter.author.id, name, file_name, version, genre_g, type_g, req, des)

            if fix is not None:
                await fix.save(f'media/torrents/{file_name}/' + fix.filename)

    @commands.slash_command(
        name='game_top',
        description='Топ игр по количеству скачиваний.',
    )
    async def game_top(self, inter: disnake.ApplicationCommandInteraction):
        games = all_games()

        emb = disnake.Embed(title='Топ игр', color=disnake.Colour.blue())
        emb.add_field(name='№', value='\n'.join([str(i) for i in range(1, len(games) + 1)]))
        emb.add_field(name='Игра', value='\n'.join([i for _, i in games]))
        emb.add_field(name='Загрузки', value='\n'.join([str(i) for i, _ in games]))

        await inter.response.send_message(embed=emb)

    @commands.slash_command(
        name='user_top',
        description='Топ пользователей по количеству активности.',
    )
    async def user_top(self, inter: disnake.ApplicationCommandInteraction):
        users = all_users()

        emb = disnake.Embed(title='Топ пользователей', color=disnake.Colour.blue())
        emb.add_field(name='Ник', value='\n'.join(['<@' + str(i) + '>' for _, _, i in users]))
        emb.add_field(name='Скачиваний', value='\n'.join([str(i) for i, _, _ in users]))
        emb.add_field(name='Добавлений', value='\n'.join([str(i) for _, i, _ in users]))

        await inter.response.send_message(embed=emb)


def setup(bot: commands.Bot):
    bot.add_cog(OtherCommand(bot))
    bot.add_cog(GameCommand(bot))
