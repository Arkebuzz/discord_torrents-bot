import disnake
from disnake.ext import commands

from config import IDS
from utils.db import DB
from utils.logger import logger


async def refresh(bot):
    """
    Обновление БД и config.py бота.

    :param bot:
    :return:
    """

    logger.info('[START] guilds refresh')

    db = DB()
    cur_guilds = [g.id for g in bot.guilds]

    if IDS != cur_guilds:
        ids = [str(g.id) for g in bot.guilds]

        with open('config.py', 'r') as f:
            text = ''
            for line in f:
                if 'IDS' in line:
                    text += 'IDS = [' + ', '.join(ids) + ']\n'
                else:
                    text += line

        with open('config.py', 'w') as f:
            f.write(text)

        import os
        import sys

        logger.warning(f'[FINISHED] guilds refresh in config : BOT RESTARTING')
        os.execv(sys.executable, [sys.executable, sys.argv[0]])

    db_guilds = [g[0] for g in db.get_guilds()]

    if db_guilds != cur_guilds:
        for guild in set(db_guilds) - set(cur_guilds):
            db.delete_guild(guild)
            logger.warning(f'[IN PROGRESS] guilds refresh : bot not in {id} but it`s in DB')

        for guild in set(cur_guilds) - set(db_guilds):
            g = bot.get_guild(guild)
            channels = (
                (g.system_channel,) if g.system_channel is not None else () +
                (g.public_updates_channel,) if g.public_updates_channel is not None else () +
                g.text_channels
            )

            for channel in channels:
                try:
                    await channel.send('Для первоначальной настройки бота используйте функцию /set_main_channel.\n'
                                       'Бот не будет корректно работать, пока Вы этого не сделаете.')
                    break
                except disnake.errors.Forbidden:
                    continue

            logger.warning(f'[IN PROGRESS] guilds refresh : {guild} not in DB -> warning sent')

    logger.info('[FINISHED] all guilds refresh')


class BotEvents(commands.Cog):
    """Класс, задающий активности на серверах."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Выполняется, когда бот запустился.

        :return:
        """

        logger.info('Bot started')
        await refresh(self.bot)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Intents.guilds):
        """
        Выполняется, когда бот присоединяется к новому серверу.

        :param guild:
        :return:
        """

        logger.info(f'[NEW GUILD] <{guild.id}>')

        await refresh(self.bot)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Intents.guilds):
        """
        Выполняется, когда бот покидает сервер.

        :param guild:
        :return:
        """

        logger.info(f'[DEL GUILD] <{guild.id}>')

        await refresh(self.bot)


def setup(bot: commands.Bot):
    """Регистрация активностей бота."""

    bot.add_cog(BotEvents(bot))
