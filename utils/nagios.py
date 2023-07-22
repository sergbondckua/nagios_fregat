import logging
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logging.basicConfig(
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-4s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)


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
        self.logger = logging.getLogger(__name__)
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

    async def fetch_data(self, session) -> str | None:
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
            return

        return await response.text()

    async def get_all_critical_hosts(self) -> list[tuple[str]]:
        """Retrieves a list of critical hosts_name from Nagios."""

        async with aiohttp.ClientSession() as session:
            html = await self.fetch_data(session)

            if html is None:
                return [("Error: Nagios authorization failed",)]

            soup = BeautifulSoup(html, "lxml")

            hosts_name = soup.find_all(
                "td",
                {
                    "class": "statusBGCRITICAL",
                    "valign": "center",
                    "align": "left",
                }
            )
            return [(self._get_one_host(host),) for host in hosts_name]

    @staticmethod
    def _get_one_host(host: BeautifulSoup) -> str:
        """Extracts the host name from a BeautifulSoup object."""

        return host.find("a").text.strip()
