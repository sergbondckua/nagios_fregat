import logging
import aiohttp
from aiogram import Bot, types
from bs4 import BeautifulSoup
from environs import Env
from fake_useragent import UserAgent

logging.basicConfig(
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-4s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)

# Read environment variables
env = Env()
env.read_env()


class GetCriticalHostNagios:
    """
    Parser for retrieving critical hosts from Nagios.

    Attributes:
        _URL (str): The URL of the Nagios status page.
        login (str): Nagios login.
        passwd (str): Nagios password.
        logger (logging.Logger): Logger instance for logging.
        headers (dict): Headers for the HTTP requests.
        params (dict): Parameters for the Nagios status page request.
        bot (aiogram.Bot): Bot instance for sending messages to Telegram.
    """

    _URL = "http://193.108.248.20/nagios/cgi-bin/status.cgi"

    def __init__(self, login, passwd):
        """
        Initializes the GetCriticalHostNagios instance.

        Args:
            login (str): Nagios login.
            passwd (str): Nagios password.
        """
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
        self.bot = Bot(
            token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)

    async def fetch_data(self, session) -> str|None:
        """Fetches data from the specified URL using the provided session."""

        response = await session.get(
            url=self._URL,
            params=self.params,
            auth=aiohttp.BasicAuth(self.login, self.passwd),
            headers=self.headers,
            timeout=3,
        )
        if response.status != 200:
            self.logger.error("Error")
            return None

        return await response.text()

    async def get_all_critical_hosts(self) -> list[tuple[str]]:
        """Retrieves a list of critical hosts_name from Nagios."""

        async with aiohttp.ClientSession() as session:
            html = await self.fetch_data(session)
            if html is None:
                return []
            soup = BeautifulSoup(html, "lxml")
            hosts_name = soup.find_all(
                "td",
                {"class": "statusBGCRITICAL", "valign": "center", "align": "left"}
            )
            return [(self._get_one_host(host),) for host in hosts_name]

    @staticmethod
    def _get_one_host(host: BeautifulSoup) -> str:
        """Extracts the host name from a BeautifulSoup object."""

        return host.find("a").text.strip()
