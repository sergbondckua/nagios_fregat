from __future__ import annotations

import aiohttp

from loader import env
from utils.log import logger


class CellSearchAPI:
    """API for searching for cells"""

    BASE_URL = env.str("URL_SEARCH_KEY")
    STREET_ENDPOINT = "street"
    CELL_ENDPOINT = "cell"

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def fetch_data(self, endpoint: str, params: dict) -> dict:
        """Fetch data from the API using aiohttp."""

        url = f"{self.BASE_URL}{endpoint}"
        async with self.session.get(url, params=params) as response:
            try:
                response.raise_for_status()
                return await response.json()
            except aiohttp.ClientResponseError as e:
                logger.warning("Error fetching data from %s:", e)

    async def get_street_id(self, street_name: str, street_prefix: str) -> str:
        """Get the street ID based on its name and prefix."""

        params = {"name": street_name, "prefix": street_prefix}
        street_info = await self.fetch_data(self.STREET_ENDPOINT, params)
        street_id = street_info.get("id") if street_info else None
        return street_id

    async def get_cell_keys(self, street_id, building_number) -> dict:
        """Get cell keys based on street ID and building number."""

        params = {"street": street_id, "number": building_number}
        return await self.fetch_data(self.CELL_ENDPOINT, params)

    async def close_session(self):
        """Close the aiohttp session."""
        await self.session.close()
