import os
import shutil

from disnake.ext import commands

from config import TOKEN, IDS
from utils.db import DB

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if os.path.isdir('media/torrents/temp'):
    shutil.rmtree('media/torrents/temp')

if not os.path.isdir('media/torrents/temp'):
    os.makedirs('media/torrents/temp')
    DB().create_db()

bot = commands.InteractionBot(test_guilds=IDS)

bot.load_extension('cogs.commands')
bot.load_extension('cogs.events')

bot.run(TOKEN)
