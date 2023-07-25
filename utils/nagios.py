import re
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from utils.log import logger


class AuthorizedException(Exception):
    """Exception raised when a user is not authorized"""


class GetCriticalHostNagios:
    """
    Parser for retrieving critical hosts from Nagios.

    Attributes:
        url (str): The URL of the Nagios status page.
        login (str): Nagios login.
        passwd (str): Nagios password.
        logger (logging.Logger): Logger instance for logging.
        headers (dict): Headers for the HTTP requests.
        params (dict): Parameters for the Nagios status page request.
    """

    def __init__(self, url: str, login: str, passwd: str):
        """
        Initializes the GetCriticalHostNagios instance.

        Args:
            url (str): The Nagios URL.
            login (str): Nagios login.
            passwd (str): Nagios password.
        """
        self.url = url
        self.login = login
        self.passwd = passwd
        self.logger = logger
        self.headers = {
            "Content-Type": "text/html; charset=UTF-8",
            "User-Agent": UserAgent().random,
        }
        self.params = {
            "hostgroup": "all",
            "style": "detail",
            "servicestatustypes": 16,
            "limit": 0,
        }

    async def fetch_data(self, session) -> str:
        """Fetches data from the specified URL using the provided session."""

        response = await session.get(
            url=self.url,
            params=self.params,
            auth=aiohttp.BasicAuth(self.login, self.passwd),
            headers=self.headers,
            timeout=3,
        )

        try:
            # Raises an exception for non-2xx status codes
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            self.logger.error("Error: %s", e)
            raise AuthorizedException from e

        return await response.text()

    async def get_all_critical_hosts(self) -> list[tuple[str, timedelta]]:
        """Retrieves a list of critical hosts and their downtime from Nagios.

        Returns:
            list[tuple[str, timedelta]]: A list of tuples containing
                the host names and their downtime as timedelta.
        """

        async with aiohttp.ClientSession() as session:
            html = await self.fetch_data(session)

            if html is None:
                return [
                    (
                        "Error: Nagios authorization failed",
                        timedelta(seconds=0),
                    ),
                ]

            soup = BeautifulSoup(html, "lxml")

            table = soup.find("table", {"class": "status"})
            critical_hosts = table.find_all("td", {"class": "statusBGCRITICAL"})

            critical_hosts_info = [
                (
                    host.find("a").text.strip(),
                    await self.parse_timedelta(downtime.text.strip()),
                )
                for host, downtime in zip(critical_hosts[::7], critical_hosts[4::7])
            ]

            return critical_hosts_info

    @staticmethod
    async def parse_timedelta(time_str: str) -> timedelta:
        """Parses the timedelta from a formatted string.

        Args:
            time_str (str): The formatted string representing the timedelta.

        Returns:
            timedelta: The parsed timedelta object.

        Raises:
            ValueError: If the input string does not match the expected format.
        """

        # Remove duplicate spaces and replace them with single spaces
        time_str = re.sub(r"\s+", " ", time_str)

        # Using a Regular Expression to Extract Numeric Values from a String
        pattern = r"(\d+)d (\d+)h (\d+)m (\d+)s"
        match = re.match(pattern, time_str)

        if match:
            days, hours, minutes, seconds = [int(x) for x in match.groups()]

            return timedelta(
                days=days, hours=hours, minutes=minutes, seconds=seconds)

        raise ValueError("Wrong time string format.")
