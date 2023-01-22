import os

from disnake.ext import commands

from config import TOKEN, IDS
from utils.db import create_db


if not os.path.isdir('media/torrents'):
    os.makedirs('media/torrents')
    create_db()

bot = commands.InteractionBot(test_guilds=IDS)
bot.load_extension('cogs.commands')


@bot.event
async def on_ready():
    print('Бот готов!')


bot.run(TOKEN)
