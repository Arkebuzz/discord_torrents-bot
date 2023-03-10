import re

import aiohttp
import aiofiles

from bs4 import BeautifulSoup


def name_conversion(name):
    """
    Изменяет вводимое название под стандарт веб-ссылки.

    :param name:
    :return:
    """

    return '-'.join(''.join([s for s in name.lower() if s not in '!"№;%:?*()-−–—_+`&’\'.,/\\']).split())


async def search_requirements(title):
    """
    Ищет системные требования игры по названию.

    :param title: Название игры.
    :return:
    """

    url = f'https://vgtimes.ru/games/{name_conversion(title)}/system-requirements/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            contents = await resp.text()

    soup = BeautifulSoup(contents, 'html.parser')
    contents = str(soup.find('div', {'class': 'req'}))

    if contents == 'None':
        contents = str(soup.find('div', {'class': 'min'}))

        if contents == 'None':
            return False

    soup = BeautifulSoup(contents, 'html.parser')
    res = ''
    for tag in soup.find_all('li'):
        res += tag.text.replace('/', '|').replace('\\', '|') + '\n'

    return res


async def search_images(title, file_name):
    """
    Ищет системные требования игры по названию.

    :param title: Название игры.
    :param file_name: Название фото.
    :return:
    """

    url = f'https://vgtimes.ru/games/{name_conversion(title)}/system-requirements/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            contents = await resp.text()

    soup = BeautifulSoup(contents, 'html.parser')

    photo = soup.find('li', {'data-thumb': re.compile(r'https://files.vgtimes.ru/gallery/thumb\S')})

    if not photo:
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(photo['data-src']) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f'media/torrents/temp/{file_name}.{resp.content_type.split("/")[-1]}',
                                            mode='wb')
                    await f.write(await resp.read())
                    await f.close()

                    return f'media/torrents/temp/{file_name}.{resp.content_type.split("/")[-1]}'

    except aiohttp.ClientConnectorError:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(photo['data-src']) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(f'media/torrents/temp/{file_name}.{resp.content_type.split("/")[-1]}',
                                                mode='wb')
                        await f.write(await resp.read())
                        await f.close()

                        return f'media/torrents/temp/{file_name}.{resp.content_type.split("/")[-1]}'

        except aiohttp.ClientConnectorError:
            return None
