import asyncio
import random
import time

from typing import Optional

import disnake
from disnake import TextInputStyle


class GameModal(disnake.ui.Modal):
    """
    Класс - модальное окно, принимает данные об игре.

    :attribute res: Значения введенные пользователем.
    :attribute inter: Объект сообщения.
    """

    def __init__(self, title, system_req='', placeholder_sr='Введите системные требования игры ...\n'):
        self.res: Optional[list[str]] = None
        self.inter: Optional[disnake.ApplicationCommandInteraction] = None
        self.time = time.time()
        self.out = 300

        components = [
            disnake.ui.TextInput(
                label='Название игры',
                custom_id='title',
                placeholder='Введите название игры ...',
                value=title
            ),
            disnake.ui.TextInput(
                label='Версия',
                custom_id='version',
                placeholder='Введите версию игры ...'
            ),
            disnake.ui.TextInput(
                label='Системные требования',
                custom_id='system_req',
                style=TextInputStyle.paragraph,
                placeholder=placeholder_sr,
                value=system_req
            ),
            disnake.ui.TextInput(
                label='Описание',
                custom_id='description',
                style=TextInputStyle.paragraph,
                placeholder='Введите описание игры или особенности репака, оставьте ссылку на обзор (необязательно)',
                required=False
            )
        ]

        super().__init__(
            title='Сведения об игре',
            custom_id=str(random.random()),
            components=components,
            timeout=self.out
        )

    async def wait(self):
        """Выполняется, пока время на ответ не истечет."""

        while self.res is None and self.inter is None and time.time() - self.time < self.out:
            await asyncio.sleep(1)

    async def callback(self, inter: disnake.ModalInteraction):
        self.res = list(inter.text_values.items())
        self.inter = inter

        await inter.response.defer(ephemeral=True)


class VoteModal(disnake.ui.Modal):
    """
    Класс - модальное окно, принимает комментарий с оценкой к игре.

    :attribute res: Значения введенные пользователем.
    :attribute inter: Объект сообщения.
    """

    def __init__(self):
        self.res = None
        self.inter = None
        self.time = time.time()
        self.out = 300

        components = [
            disnake.ui.TextInput(
                label='Ваша оценка (число от 1 до 5)',
                custom_id='score',
                placeholder='Оцените игру ...',
                max_length=1
            ),
            disnake.ui.TextInput(
                label='Комментарий',
                custom_id='comment',
                style=TextInputStyle.paragraph,
                placeholder='Напишите отзыв об игре ...',
                required=False
            )
        ]

        super().__init__(
            title='Добавление отзыва',
            custom_id=str(random.random()),
            components=components,
            timeout=self.out
        )

    async def wait(self):
        """Выполняется, пока время на ответ не истечет."""

        while self.res is None and self.inter is None and time.time() - self.time < self.out:
            await asyncio.sleep(1)

    async def callback(self, inter: disnake.ModalInteraction):
        self.res = list(inter.text_values.items())
        self.inter = inter

        await inter.response.defer(ephemeral=True)
