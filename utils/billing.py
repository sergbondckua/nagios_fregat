import asyncio

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from loader import env


class BillingUserData:
    """Pass"""

    def __init__(self, url, login: str, passwd: str) -> None:
        """
        Initialize the BillingUserData object.

        Parameters:
            url (str): Billing URL.
            login (str): The login for authentication.
            passwd (str): The password for authentication.
        """
        self.url = url
        self.timeout = ClientTimeout(total=10)
        self.connector = TCPConnector(limit_per_host=10)
        self.headers = {"User-Agent": UserAgent().chrome}
        self.data = {"enter": "do", "uu": login, "pp": passwd}
        self.session = None

    async def fetch_data(self, url: str, params: dict[str, str]) -> str:
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

    async def get_profile_link(self, user: str) -> str:
        """
        Get the profile link for the given user.

        Parameters:
            user (str): The username to find the profile link.

        Returns:
            str: The profile link URL.
        """

        url = f"{self.url}/cgi-bin/adm/adm.pl"
        params = {"a": "listuser", "id": "", "name": user}
        html = await self.fetch_data(url, params)

        soup = BeautifulSoup(html, "lxml")
        rows = soup.find("table", {"class": "zebra"}).find_all("tr")[2:]
        link_user = self.url + rows[0].find("a").get("href")
        url_profile = f"{link_user}&username={user}"

        return url_profile

    async def get_credentials_user(self, url_profile: str) -> dict[str, str]:
        """
        Get the credentials for the user from the profile URL.

        Parameters:
            url_profile (str): The user's profile URL.

        Returns:
            dict: A dictionary containing user credentials.
        """

        params = {"act": "blank"}
        html = await self.fetch_data(url_profile, params)
        soup = BeautifulSoup(html, "lxml")
        credentials = {}

        for row in soup.find("table", {"class": "content"}).find_all("tr"):
            cells = row.find_all(["td", "b"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                credentials[key] = value
        # await self.close_session()

        return credentials

    async def get_seance_user(
        self, url_profile: str, rows: int = 10
    ) -> list[dict]:
        """
        Fetches seance user data from a given URL.

        Args:
            url_profile (str): The URL to fetch the seance user data from.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing seance user information.
                                  Each dictionary represents one row of the data with the following keys:
                                  - 'start': Start time of the seance.
                                  - 'end': End time of the seance.
                                  - 'ip': IP address of the user.
                                  - 'nas': NAS (Network Access Server) information.
                                  - 'mac': MAC (Media Access Control) address of the user.
                                  - 'reason': Reason for the seance.
                                  - 'vlan': VLAN (Virtual LAN) information.
                                  - 'port': Port number associated with the seance.
        """
        params = {"act": "seance"}
        html = await self.fetch_data(url_profile, params)
        soup = BeautifulSoup(html, "lxml")
        rows = soup.find("table", {"class": "zebra-small"}).find_all("tr")[
            1:rows
        ]

        title = ["start", "end", "ip", "nas", "mac", "reason", "vlan", "port"]

        seance = []
        for row in rows:
            cols = [
                col.text.strip().replace("\xa0\xa0\xa0", " ")
                for col in row.find_all("td")
            ]
            make_dict = dict(zip(title, cols))
            seance.append(make_dict)

        return seance

    async def close_session(self) -> None:
        """Close the ClientSession if it is active."""

        if self.session:
            await self.session.close()


async def main():
    bill = BillingUserData(
        url=env.str("URL_BILLING"),
        login=env.str("LOGIN_BILLING"),
        passwd=env.str("PASSWD_BILLING"),
    )
    link = await bill.get_profile_link("chk_ninja")
    blank = await bill.get_credentials_user(link)
    seance = await bill.get_seance_user(link)
    await bill.close_session()
    print(blank, seance, sep="\n")


if __name__ == "__main__":
    asyncio.run(main())
