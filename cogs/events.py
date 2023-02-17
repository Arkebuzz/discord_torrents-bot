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
    db_guilds = [g[0] for g in db.get_guilds()]

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

    if db_guilds != cur_guilds:
        for guild_id in set(db_guilds) - set(cur_guilds):
            db.delete_guild(guild_id)
            logger.warning(f'[IN PROGRESS] guilds refresh : bot not in {id} but it`s in DB')

        for guild_id in set(cur_guilds) - set(db_guilds):
            logger.info(f'[IN PROGRESS] guilds refresh : {guild_id} not in DB -> starting messages analyze')

            db.update_guild_settings(guild_id)

            logger.info(f'[IN PROGRESS] guilds refresh : {guild_id} not in DB -> messages are analyzed')

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

        for channel in guild.text_channels:
            try:
                await channel.send('Здравствуйте, я очень рад, что вы добавили меня на сервер.')

                emb = disnake.Embed(
                    description='Я умею получать от вас торренты игр и присылать вам, когда они вам понадобятся.\n\n'
                                'Описание команд'
                )

                emb.add_field('Команда', '\n'.join(com.name for com in self.bot.slash_commands))
                emb.add_field('Описание', '\n'.join(com.description for com in self.bot.slash_commands))

                await channel.send(embed=emb)

                await channel.send('Если вам нужны оповещения о новых играх, которые добавили боту, то выберите для '
                                   'них  канал командой /set_main_channel')

                logger.info(f'[NEW GUILD] <{guild.id}> -> welcome message sent')
                break
            except disnake.errors.Forbidden:
                continue

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
