from typing import Optional

import disnake

from config import TYPE_OPTIONS, GENRE_OPTIONS


class SelectGameType(disnake.ui.View):
    """
    Класс добавляет к сообщению меню с выбором типа игры.

    :attribute value: Выбор пользователя.
    """

    def __init__(self):
        super().__init__(timeout=60)
        self.value: Optional[str] = None

    @disnake.ui.string_select(placeholder='Выберите типы игры ...',
                              max_values=len(TYPE_OPTIONS),
                              options=[disnake.SelectOption(label=lab, description=d) for lab, d in TYPE_OPTIONS])
    async def select(self, string_select: disnake.ui.StringSelect, inter: disnake.ApplicationCommandInteraction):
        self.value = string_select.values
        self.stop()

        await inter.response.defer()


class SelectGameGenre(disnake.ui.View):
    """
    Класс добавляет к сообщению меню с выбором жанра игры.

    :attribute value: Выбор пользователя.
    """

    def __init__(self):
        super().__init__(timeout=60)
        self.value: Optional[str] = None

    @disnake.ui.string_select(placeholder='Выберите жанры игры ...',
                              max_values=len(GENRE_OPTIONS),
                              options=[disnake.SelectOption(label=lab[0]) for lab in GENRE_OPTIONS])
    async def select(self, string_select: disnake.ui.StringSelect, inter: disnake.ApplicationCommandInteraction):
        self.value = string_select.values
        self.stop()

        await inter.response.defer()
