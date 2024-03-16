import asyncio
import aiohttp
from utils.log import logger


async def fetch_company_name(
    mac_address: str, session: aiohttp.ClientSession
) -> str:
    """Fetches company name associated with a MAC address."""
    url = f"https://api.macvendors.com/{mac_address}"
    try:
        async with session.get(url, ssl=False) as response:
            response.raise_for_status()
            company_name = (await response.text()).capitalize().split(" ")[0]
            return company_name
    except aiohttp.ClientResponseError as e:
        logger.error("Error fetching data from %s:", e)
        return str(e.message).replace(" ", "_")


async def add_company_name_to_mac_data(data: list) -> None:
    """Adds company name to the list of MAC addresses."""
    used_mac_addresses = set()
    async with aiohttp.ClientSession() as session:
        for item in data:
            mac_address = item["mac"]
            if mac_address not in used_mac_addresses:
                used_mac_addresses.add(mac_address)
                company_name = await fetch_company_name(mac_address, session)
                item["mac_company_name"] = company_name
                await asyncio.sleep(1)
            else:
                item["mac_company_name"] = company_name
