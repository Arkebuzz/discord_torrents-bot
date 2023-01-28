import os

from disnake.ext import commands

from config import TOKEN, IDS
from utils.db import create_db

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if not os.path.isdir('media/torrents'):
    os.makedirs('media/torrents')
    create_db()

from utils.logger import logger
from cogs.events import refresh

bot = commands.InteractionBot(test_guilds=IDS)

bot.load_extension('cogs.commands')
bot.load_extension('cogs.events')


@bot.event
async def on_ready():
    logger.info('Bot started')
    await refresh(bot)


bot.run(TOKEN)
