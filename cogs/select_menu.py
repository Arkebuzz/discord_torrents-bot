from typing import Optional

import disnake

GENRE_OPTION = ['стратегия',
                'рпг',
                'шутер',
                'хоррор',
                'файтинг',
                'выживание',
                'экшен',
                'гонки',
                'открытый мир',
                ]
TYPE_OPTION = [('одиночная игра', 'Есть возможность одиночной игры.'),
               ('онлайн (LAN)', 'Есть возможность играть онлайн без Steam.'),
               ('онлайн (Steam)', 'Есть возможность играть онлайн через Steam.'),
               ]


class SelectGameType(disnake.ui.View):
    """
    Класс добавляет к сообщению меню с выбором типа игры.

    :param followup: Удалить за собой сообщение?
    :attribute value: Выбор пользователя.
    """

    def __init__(self, followup=False):
        super().__init__(timeout=60)
        self.value: Optional[str] = None
        self.followup = followup

    @disnake.ui.string_select(placeholder='Выберите типы игры ...',
                              min_values=0,
                              max_values=3,
                              options=[disnake.SelectOption(label=l, description=d) for l, d in TYPE_OPTION])
    async def select(self, string_select: disnake.ui.StringSelect, inter: disnake.ApplicationCommandInteraction):
        self.value = string_select.values
        self.stop()

        await inter.response.defer()
        if self.followup:
            await inter.delete_original_response()


class SelectGameGenre(disnake.ui.View):
    """
    Класс добавляет к сообщению меню с выбором жанра игры.

    :param followup: Удалить за собой сообщение?
    :attribute value: Выбор пользователя.
    """

    def __init__(self, followup=False):
        super().__init__(timeout=60)
        self.value: Optional[str] = None
        self.followup = followup

    @disnake.ui.string_select(placeholder='Выберите жанры игры ...',
                              min_values=0,
                              max_values=9,
                              options=[disnake.SelectOption(label=l) for l in GENRE_OPTION])
    async def select(self, string_select: disnake.ui.StringSelect, inter: disnake.ApplicationCommandInteraction):
        self.value = string_select.values
        self.stop()

        await inter.response.defer()
        if self.followup:
            await inter.delete_original_response()
