import disnake


class Flipping(disnake.ui.View):
    """
    Класс добавляет к сообщению 3 кнопки: вперёд, назад и скачать.

    :param mx: Количество страниц.
    :param value: Стартовая страница.
    :attribute res: Значение текущей страницы.
    """

    def __init__(self, mx, value=0):
        super().__init__(timeout=60)
        self.value = value
        self.res = None
        self.mx = mx

    @disnake.ui.button(label='Назад', style=disnake.ButtonStyle.grey)
    async def left(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = self.value - 1
        if self.res < -self.mx:
            self.res = self.mx - 1

        await inter.response.defer()
        # await inter.delete_original_response()

        self.stop()

    @disnake.ui.button(label='Вперёд', style=disnake.ButtonStyle.grey)
    async def right(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = self.value + 1
        if self.res >= self.mx:
            self.res = 0

        await inter.response.defer()
        # await inter.delete_original_response()

        self.stop()

    @disnake.ui.button(label='Скачать', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
        self.res = str(self.res) if self.res is not None else str(self.value)
        self.stop()
