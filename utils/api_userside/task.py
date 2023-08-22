import asyncio

import aiohttp

from loader import env


class ApiUsersideData:
    """tODO: implement"""

    def __init__(self, api_key):
        self.url = env.str("URL_USERSIDE")
        self.api_key = api_key
        self.params = {}

    async def fetch_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def get_task(self, task_id):
        url = f"{self.url}api.php?key={self.api_key}&cat=task&action=show&id={task_id}"
        data = await self.fetch_data(url)
        print(data, type(data))


async def main():
    await ApiUsersideData(env.str("API_KEY")).get_task(27761)


if __name__ == "__main__":
    asyncio.run(main())
