import os

import disnake
from disnake.ext import commands

from config import TOKEN, IDS
from utils.db import create_db, add_reaction, del_reaction

if not os.path.isdir('media/torrents'):
    os.makedirs('media/torrents')
    create_db()

from utils.logger import logger

bot = commands.InteractionBot(test_guilds=IDS)
bot.load_extension('cogs.commands')


@bot.event
async def on_ready():
    logger.info('Bot started')


@bot.event
async def on_raw_reaction_add(payload: disnake.RawReactionActionEvent):
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


@bot.event
async def on_raw_reaction_remove(payload: disnake.RawReactionActionEvent):
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


bot.run(TOKEN)
