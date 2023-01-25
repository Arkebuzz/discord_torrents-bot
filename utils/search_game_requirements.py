import aiohttp
from bs4 import BeautifulSoup


async def search_requirements(title):
    name = ''
    f = False

    for i in title:
        if f and i != ' ' and i not in '!"№;%:?*()_+\'.,/\\':
            name += '-' + i

        elif f and i == ' ':
            f = False
        elif i == ' ':
            name += '-'
        elif i in '-−–—':
            f = True
        elif i not in '!"№;%:?*()_+\'.,':
            name += i

    url = f'https://vgtimes.ru/games/{name}/system-requirements/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            contents = await resp.text()

    soup = BeautifulSoup(contents, 'html.parser')
    contents = str(soup.find('div', {'class': 'req'}))

    if contents == 'None':
        url = f'https://vgtimes.ru/games/{name}/system-requirements/'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                contents = await resp.text()

        soup = BeautifulSoup(contents, 'html.parser')
        contents = str(soup.find('div', {'class': 'min'}))

        if contents == 'None':
            return False

    soup = BeautifulSoup(contents, 'html.parser')
    res = ''
    for tag in soup.find_all('li'):
        res += tag.text.replace('/', '|').replace('\\', '|') + '\n'

    return res
