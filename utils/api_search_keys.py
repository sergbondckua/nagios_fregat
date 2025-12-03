from __future__ import annotations
import aiohttp

from loader import env
from utils.log import logger


class CellSearchAPI:
    """API для пошуку вулиць та ключів клітин."""

    BASE_URL = env.str(
        "URL_SEARCH_KEY"
    )  # Наприклад: "http://internal_service_platform:8001/api/v1/"
    STREET_ENDPOINT = "street"
    CELL_ENDPOINT = "cell"

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def fetch_data(self, endpoint: str, params: dict) -> dict | None:
        """
        Робить GET запит до API з переданими параметрами.

        aiohttp автоматично кодує params, тому вручну кодувати не потрібно.
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()  # Викликає виняток при 4xx/5xx
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logger.warning("Error fetching data from %s: %s", url, e)
        except Exception as e:
            logger.warning(
                "Unexpected error fetching data from %s: %s", url, e
            )

        return None

    async def get_street_id(
        self, street_name: str, street_prefix: str
    ) -> str | None:
        """
        Отримує ID вулиці за назвою та префіксом.
        Повертає None, якщо вулицю не знайдено.
        """
        params = {"name": street_name, "prefix": street_prefix}
        street_info = await self.fetch_data(self.STREET_ENDPOINT, params)
        return street_info.get("id") if street_info else None

    async def get_cell_keys(
        self, street_id: str, building_number: str
    ) -> dict | None:
        """
        Отримує ключі клітин по ID вулиці та номеру будинку.
        Повертає None, якщо дані не отримані.
        """
        if not street_id:
            logger.warning("Street ID is None. Cannot fetch cell keys.")
            return None

        params = {"street": street_id, "number": building_number}
        return await self.fetch_data(self.CELL_ENDPOINT, params)

    async def close_session(self):
        """Закриває aiohttp сесію."""
        await self.session.close()
