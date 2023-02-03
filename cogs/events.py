import disnake
from disnake.ext import commands

from config import IDS
from utils.db import guild_remove
from utils.logger import logger


async def refresh(bot):
    """
    Обновление БД и config.py бота.

    :param bot:
    :return:
    """

    logger.info('[START] guilds refresh')

    guilds = [g.id for g in bot.guilds]

    if IDS != guilds:
        for guild in set(IDS) - set(guilds):
            guild_remove(guild)
            logger.warning(f'[IN PROGRESS] guilds refresh : bot not in {guild.id}')

        for guild in set(guilds) - set(IDS):
            g = bot.get_guild(guild)

            for channel in g.text_channels:
                try:
                    await channel.send('Для первоначальной настройки бота используйте функцию /option.\n'
                                       'Бот не будет корректно работать, пока Вы этого не сделаете.')
                    break
                except disnake.errors.Forbidden:
                    continue

            logger.warning(f'[IN PROGRESS] guilds refresh : {guild} not in DB -> warning sent')

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

        logger.warning(f'[FINISHED] guilds refresh : BOT RESTARTING')

        os.execv(sys.executable, [sys.executable, sys.argv[0]])

    logger.info('[FINISHED] guilds refresh')


class BotEvents(commands.Cog):
    """Класс, задающий активности на серверах."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
