import disnake
from disnake.ext import commands

from config import IDS
from utils.db import add_reaction, del_reaction, get_guilds
from utils.logger import logger


async def refresh(bot):
    logger.info('[START] guilds refresh')
    flag = False

    for guild in bot.guilds:
        if guild.id not in IDS:
            flag = True
            IDS.append(guild.id)

            logger.info(f'[IN PROGRESS] guilds refresh : {guild.id} not in IDS -> append')

        if not get_guilds(guild.id):

            g = bot.get_guild(guild.id)

            for channel in g.text_channels:
                try:
                    await channel.send('Для первоначальной настройки бота используйте функцию /option.\n'
                                       'Бот не будет корректно работать, пока Вы этого не сделаете.')
                    break
                except disnake.errors.Forbidden:
                    continue

            logger.warning(f'[IN PROGRESS] guilds refresh : {guild.id} not in DB -> warning sent')

    ids = map(str, IDS)

    with open('config.py', 'r') as f:
        text = ''
        for line in f:
            if 'IDS' in line:
                text += 'IDS = [' + ', '.join(ids) + ']\n'
            else:
                text += line

    with open('config.py', 'w') as f:
        f.write(text)

    if flag:
        logger.warning('[FINISHED] guilds refresh NEED RESTART')

        import os
        import sys

        os.execv(sys.executable, [sys.executable, __file__] + sys.argv)

    else:
        logger.info('[FINISHED] guilds refresh')


class BotEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Intents.guilds):
        await refresh(self.bot)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
        if payload.user_id == 1065653420364660766:
            return

        emoji = str(payload.emoji)
        if emoji in '1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣':
            if emoji == '1️⃣':
                emoji = 1
            elif emoji == '2️⃣':
                emoji = 2
            elif emoji == '3️⃣':
                emoji = 3
            elif emoji == '4️⃣':
                emoji = 4
            else:
                emoji = 5

            if add_reaction(payload.message_id, payload.user_id, emoji):
                logger.info(f'[NEW REACT] {payload.user_id} {emoji}')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: disnake.RawReactionActionEvent):
        if payload.user_id == 1065653420364660766:
            return

        emoji = str(payload.emoji)
        if emoji in '1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣':
            if emoji == '1️⃣':
                emoji = 1
            elif emoji == '2️⃣':
                emoji = 2
            elif emoji == '3️⃣':
                emoji = 3
            elif emoji == '4️⃣':
                emoji = 4
            else:
                emoji = 5

            if del_reaction(payload.message_id, payload.user_id, emoji):
                logger.info(f'[DEL REACT] {payload.user_id} {emoji}')


def setup(bot: commands.Bot):
    bot.add_cog(BotEvents(bot))
