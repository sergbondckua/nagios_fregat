import asyncio
import urllib.parse

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from loader import env
from utils.log import logger


class BillingUserData:
    """Represents user data for billing."""

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
        self.data = {"enter": "do", "uu": login, "pp": passwd}
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

    async def get_profile_link(self, user_login: str) -> str:
        """
        Get the profile link for the given user.

        Parameters:
            user_login (str): The username to find the profile link.

        Returns:
            str: The profile link URL.
        """

        url = f"{self.url}/cgi-bin/adm/adm.pl"
        params = {"a": "listuser", "name": user_login}
        html = await self._fetch_data(url, params)
        soup = BeautifulSoup(html, "lxml")

        try:
            rows = soup.find("table", {"class": "zebra"}).find_all("tr")[2:]
        except AttributeError as exp:
            # If 'soup.find' or any attribute extraction fails, it means the user doesn't exist.
            raise ValueError(
                f"The user '{user_login}' does not exist."
            ) from exp

        link_user = self.url + rows[0].find("a").get("href")
        url_profile = f"{link_user}&username={user_login}"
        logger.info("Profile URL: %s", url_profile)

        return url_profile

    async def find_user_data(
        self, params: dict[str, str]
    ) -> list[dict[str, str]]:
        """Fetch user data from the billing system using the given parameters.

        Parameters:
            params (dict): The query parameters for the request.

        Returns:
            list[dict]: A list of dictionaries containing user data.
        """

        url = f"{self.url}/cgi-bin/adm/adm.pl"
        html = await self._fetch_data(url, params)
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select("table.zebra tr")
        data = []

        for row in rows:
            columns = row.select("td")
            if len(columns) >= 8:
                date_time = columns[0].text.strip()
                login = columns[1].select("b")[0].text.strip()
                url_profile = columns[1].select("a")[0].get("href").strip()
                full_name = columns[2].select("b")[0].text.strip()
                address = columns[3].text.strip()
                group = columns[4].text.strip()
                packet = columns[5].text.strip()
                balance_without = columns[6].text.strip()
                balance_with = columns[7].text.strip()

                data.append(
                    {
                        "date": date_time,
                        "login": login,
                        "url_profile": f"{self.url}{url_profile}&username={login}",
                        "full_name": full_name,
                        "address": address,
                        "group": group,
                        "packet": packet,
                        "balance_without": balance_without,
                        "balance_with": balance_with,
                    }
                )
        return data

    async def find_by_login(self, user_login: str) -> list[dict[str, str]]:
        """
        Find users by their login.

        Args:
            user_login (str): The login name of the user.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing user data.
        """
        params = {"a": "listuser", "name": user_login}

        return await self.find_user_data(params)

    async def find_by_fio(self, full_name: str) -> list[dict[str, str]]:
        """
        Find users by their full name.

        Args:
            full_name (str): The full name of the user.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing user data.
        """
        url_encoded_full_name = urllib.parse.quote(full_name, encoding="cp1251")
        params = {"a": "listuser", "fio": url_encoded_full_name}

        return await self.find_user_data(params)

    async def find_by_login_or_fio(self, user_query: str) -> list:
        """Find users by login or full name.
    Args:
        user_query (str): The query string representing either a login or a full name.

    Returns:
        list: A list of users that match the provided query.
    """

        by_login = await self.find_by_login(user_query)
        if by_login:
            return by_login

        return await self.find_by_fio(user_query)

    async def get_credentials_user(self, url_profile: str) -> dict[str, str]:
        """
        Get the credentials for the user from the profile URL.

        Parameters:
            url_profile (str): The user's profile URL.

        Returns:
            dict: A dictionary containing user credentials.
        """

        params = {"act": "blank"}
        html = await self._fetch_data(url_profile, params)
        soup = BeautifulSoup(html, "lxml")
        credentials = {}

        for row in soup.find("table", {"class": "content"}).find_all("tr"):
            cells = row.find_all(["td", "b"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                credentials[key] = value

        return credentials

    async def get_session_user(
        self, url_profile: str, rows: int = 11
    ) -> list[dict]:
        """
        Fetches session user data from a given URL.

        Args:
            url_profile (str): The URL to fetch the session user data from.
            rows (str): Slice list

        Returns:
            list[dict[str, str]]: A list of dictionaries containing session user information.
                Each dictionary represents one row of the data with the following keys:
                - 'start': Start time of the session.
                - 'end': End time of the session.
                - 'ip': IP address of the user.
                - 'nas': NAS (Network Access Server) information.
                - 'mac': MAC (Media Access Control) address of the user.
                - 'reason': Reason for the session.
                - 'vlan': VLAN (Virtual LAN) information.
                - 'port': Port number associated with the session."""

        params = {"act": "seance"}
        html = await self._fetch_data(url_profile, params)
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

    async def get_balance_user(self, url_profile: str) -> dict[str, str]:
        """
            Retrieve user balance and related information.

        Args:
            url_profile (str): The URL of the user's profile.

        Returns:
            dict[str, str]: A dictionary containing user data with the following keys:
                - "Користувач": The name of the user.
                - "ППК": The user's account number.
                - "Зняття за період": Withdrawal amount for the period.
                - "Баланс": The current balance of the user.
        """

        params = {}
        html = await self._fetch_data(url_profile, params)
        soup = BeautifulSoup(html, "lxml")

        # Initialize an empty dictionary
        user_data = {}
        # Get all content elements within the div with class 'data_small'
        contents = soup.find("div", class_="data_small").contents

        # Extract relevant information and store in the dictionary
        user_data["Користувач"] = contents[0].text.split(": ")[1]
        user_data["ППК"] = contents[2].text.split(": ")[1]
        user_data["Зняття за період"] = contents[4].text.split(": ")[1]
        user_data["Баланс"] = contents[6].text.split(": ")[1]

        return user_data

    async def close_session(self) -> None:
        """Close the ClientSession if it is active."""

        if self.session:
            await self.session.close()


async def main():
    async with BillingUserData(
        url=env.str("URL_BILLING"),
        login=env.str("LOGIN_BILLING"),
        passwd=env.str("PASSWD_BILLING"),
    ) as bill:
        # fio = await bill.find_by_fio("Оксаниченко")
        # login = await bill.find_by_login("chk_oks")
        data = await bill.find_by_login_or_fio("chk_oks")

    print(
        data,
        # fio,
        # login,
        sep="\n\n",
    )


if __name__ == "__main__":
    asyncio.run(main())
