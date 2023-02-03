from typing import Optional

import disnake


class Flipping(disnake.ui.View):
    """
    Класс добавляет к сообщению 2 кнопки: вперёд и назад.

    :param mx: Количество страниц.
    :param current: Стартовая страница.
    :attribute value: Значение текущей страницы.
    """

    def __init__(self, mx, current=0):
        super().__init__(timeout=300)
        self.current = current
        self.value = None
        self.mx = mx - 1

    def stop(self):
        self.value = self.current if self.value is None else self.value
        super().stop()

    @disnake.ui.button(label='Назад', style=disnake.ButtonStyle.grey)
    async def left(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        if self.current < 1:
            self.value = self.mx
        else:
            self.value = self.current - 1

        await inter.response.defer()
        self.stop()

    @disnake.ui.button(label='Вперёд', style=disnake.ButtonStyle.grey)
    async def right(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        if self.current >= self.mx:
            self.value = 0
        else:
            self.value = self.current + 1

        await inter.response.defer()
        self.stop()


class GameList(Flipping):
    """
    Класс добавляет к сообщению 5 кнопки: вперёд, назад, оценить, комментарии, скачать.

    :param mx: Количество страниц.
    :param value: Стартовая страница.
    :attribute value: Значение текущей страницы.
    :attribute res: Выбор пользователя.
    :attribute inter: Объект сообщения.
    """

    def __init__(self, mx, value=0):
        super().__init__(mx, value)
        self.res: Optional[str] = None
        self.inter: Optional[disnake.ApplicationCommandInteraction] = None

    @disnake.ui.button(label='Оценить', style=disnake.ButtonStyle.green)
    async def vote(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = 'v'
        self.inter = inter
        self.stop()

    @disnake.ui.button(label='Комментарии', style=disnake.ButtonStyle.green)
    async def comments(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = 'c'
        self.inter = inter
        self.stop()

    @disnake.ui.button(label='Скачать', style=disnake.ButtonStyle.green)
    async def download(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = 'd'
        self.inter = inter
        self.stop()


class CommentsList(Flipping):
    """
    Класс добавляет к сообщению 5 кнопки: вперёд, назад, оценить, комментарии, скачать.

    :param mx: Количество страниц.
    :param value: Стартовая страница.
    :attribute value: Значение текущей страницы.
    :attribute res: Выбор пользователя.
    """

    def __init__(self, mx, value=0):
        super().__init__(mx, value)
        self.res: Optional[str] = None

    @disnake.ui.button(label='Вернуться к поиску', style=disnake.ButtonStyle.green)
    async def download(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        self.res = 'r'
        self.stop()
