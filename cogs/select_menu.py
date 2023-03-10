from typing import Optional

import disnake

from config import TYPE_OPTIONS, GENRE_OPTIONS

type_options = [t[0] for t in TYPE_OPTIONS]


class SelectGameType(disnake.ui.View):
    """
    Класс добавляет к сообщению меню с выбором типа игры.

    :attribute value: Выбор пользователя.
    """

    def __init__(self):
        super().__init__(timeout=60)
        self.value: Optional[list[int]] = None

    @disnake.ui.string_select(placeholder='Выберите типы игры ...',
                              max_values=len(TYPE_OPTIONS),
                              options=[disnake.SelectOption(label=lab, description=d) for lab, d in TYPE_OPTIONS])
    async def select(self, string_select: disnake.ui.StringSelect, inter: disnake.ApplicationCommandInteraction):
        if string_select.values is None:
            self.value = None
        else:
            self.value = [type_options.index(t) + 100 for t in string_select.values]

        self.stop()
        await inter.response.defer()


class SelectGameGenre(disnake.ui.View):
    """
    Класс добавляет к сообщению меню с выбором жанра игры.

    :attribute value: Выбор пользователя.
    """

    def __init__(self):
        super().__init__(timeout=60)
        self.value: Optional[list[int]] = None

    @disnake.ui.string_select(placeholder='Выберите жанры игры ...',
                              max_values=len(GENRE_OPTIONS),
                              options=[disnake.SelectOption(label=lab) for lab in GENRE_OPTIONS])
    async def select(self, string_select: disnake.ui.StringSelect, inter: disnake.ApplicationCommandInteraction):
        if string_select.values is None:
            self.value = None
        else:
            self.value = [GENRE_OPTIONS.index(g) for g in string_select.values]

        self.stop()
        await inter.response.defer()
