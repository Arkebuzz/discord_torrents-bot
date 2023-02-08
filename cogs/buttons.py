from typing import Optional

import disnake


class Confirm(disnake.ui.View):
    """
    Класс добавляет к сообщению 2 кнопки: продолжить и отменить.
    """

    def __init__(self):
        super().__init__(timeout=300)
        self.res: Optional[str] = None

    @disnake.ui.button(label='Перейти к поиску', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = 'search'
        await inter.response.defer()
        self.stop()

    @disnake.ui.button(label='Добавить игру', style=disnake.ButtonStyle.green)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = 'new_game'
        await inter.response.defer()
        self.stop()


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
        self.value: Optional[int] = None
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
        self.res = 'vote'
        self.inter = inter
        self.stop()

    @disnake.ui.button(label='Комментарии', style=disnake.ButtonStyle.green)
    async def comments(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = 'comments'
        self.inter = inter
        self.stop()

    @disnake.ui.button(label='Скачать', style=disnake.ButtonStyle.green)
    async def download(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = 'download'
        self.inter = inter
        self.stop()


class FlippingBack(Flipping):
    """
    Класс добавляет к сообщению 5 кнопки: вперёд, назад и вернуться к поиску.

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
        self.res = 'r'
        await inter.response.defer()
        self.stop()
