from aiohttp import ClientSession, ClientTimeout, TCPConnector
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class GetUserside:
    """This class receives the functionality of the Userside"""

    def __init__(self, url, login: str, passwd: str) -> None:
        """
        Initialize the BillingUserData object.

        Parameters:
            url (str): Billing URL.
            login (str): The login for authentication.
            passwd (str): The password for authentication.
        """
        self.url = url
        self.timeout = ClientTimeout(total=20)
        self.connector = TCPConnector(ssl=False, limit_per_host=10)
        self.headers = {"User-Agent": UserAgent().chrome}
        self.data = {"us_oper_login": login, "us_oper_pass": passwd}
        self.session = None

    async def __aenter__(self):
        """Async context manager entry point."""

        self.session = ClientSession(
            timeout=self.timeout, connector=self.connector, headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async context manager exit point."""

        await self.session.close()

    async def _fetch_data(self, url: str, params: dict[str, str]) -> str:
        """
        Fetch data from the given URL with the specified parameters.
    
        Parameters:
            url (str): The URL to fetch data from.
            params (dict): The query parameters for the request.
    
        Returns:
            str: The response text.
        """
    
        if self.session is None:
            self.session = ClientSession(
                timeout=self.timeout, connector=self.connector
            )
        async with self.session.post(
            url, headers=self.headers, params=params, data=self.data
        ) as response:
            return await response.text()


if __name__ == "__main__":
    userside = GetUserside(
        "http://00/adminlogin.php", "xxx", "xxx"
    )
