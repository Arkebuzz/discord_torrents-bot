import re

import aiohttp
import aiofiles

from bs4 import BeautifulSoup


def name_conversion(name):
    res = ''
    f = False

    for i in name:
        if f and i != ' ' and i not in '!"№;%:?*()_+\'.,/\\':
            res += '-' + i
            f = False
        elif f and i == ' ':
            f = False
        elif i == ' ':
            res += '-'
        elif i in '-−–—':
            f = True
        elif i not in '!"№;%:?*()_+\'.,':
            res += i

    return res


async def search_requirements(title):
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


async def search_images(title, file):
    url = f'https://vgtimes.ru/games/{name_conversion(title)}/system-requirements/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            contents = await resp.text()

    soup = BeautifulSoup(contents, 'html.parser')

    photo = soup.find('li', {'data-thumb': re.compile(r'https://files.vgtimes.ru/gallery/thumb\S')})

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(photo['data-src']) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f'media/torrents/{file}/img.{resp.content_type.split("/")[-1]}', mode='wb')
                    await f.write(await resp.read())
                    await f.close()
    except aiohttp.ClientConnectorError:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(photo['data-src']) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(f'media/torrents/{file}/img.{resp.content_type.split("/")[-1]}',
                                                mode='wb')
                        await f.write(await resp.read())
                        await f.close()
        except aiohttp.ClientConnectorError:
            pass
