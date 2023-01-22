import random
import asyncio

import disnake
from disnake import TextInputStyle


class NewGameModal(disnake.ui.Modal):
    """
    Класс - модальное окно

    :attribute res: Значения введенные пользователем.
    """

    def __init__(self, title, system_req):
        self.res = None

        components = [
            disnake.ui.TextInput(
                label='Название игры',
                custom_id='title',
                placeholder='Supreme Commander: Forged Alliance',
                value=title
            ),
            disnake.ui.TextInput(
                label='Версия',
                custom_id='version',
                placeholder='v1.0.5'
            ),
            disnake.ui.TextInput(
                label='Системные требования',
                custom_id='system_req',
                style=TextInputStyle.paragraph,
                placeholder='Например:\n'
                            'CPU: Pentium 4 @ 1.8 GHz\n'
                            'GPU: GeForce 6000 / better с 128 MB памяти\n...',
                value=system_req
            ),
            disnake.ui.TextInput(
                label='Описание',
                custom_id='description',
                style=TextInputStyle.paragraph,
                placeholder='Введите описание игры или особенности репака (необязательно)',
                required=False
            )
        ]

        super().__init__(
            title='Сведения об игре',
            custom_id=str(random.random()),
            components=components,
        )

    async def wait(self):
        while self.res is None:
            await asyncio.sleep(1)

    async def callback(self, inter: disnake.ModalInteraction):
        self.res = list(inter.text_values.items())

        await inter.response.defer()
        await inter.delete_original_response()
