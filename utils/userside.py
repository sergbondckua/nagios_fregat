import requests
from bs4 import BeautifulSoup
from loader import env


class UsersideWebDataFetcher:
    """
    A class for fetching user and switch information from a web-based service.
    """

    def __init__(self, base_url: str, login: str, password: str):
        """
        Initialize the UsersideWebDataFetcher instance.

        :param base_url: The base URL of the web-based service.
        :param login: The login username for authentication.
        :param password: The password for authentication.
        """
        self.base_url = base_url
        self.username = login
        self.password = password
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def authenticate(self) -> bool:
        """
        Authenticate the user with the provided credentials.

        :return: True if authentication is successful, False otherwise.
        """
        login_url = f"{self.base_url}/adminlogin.php"
        payload = {
            "us_oper_login": self.username,
            "us_oper_pass": self.password,
        }
        response = self.session.post(login_url, data=payload)

        return "login_page_alert" not in response.text

    def _fetch_page(self, link: str) -> str:
        """
        Fetch the content of a web page.

        :param link: The relative URL of the page.
        :return: The HTML content of the page.
        """
        full_url = f"{self.base_url}/oper/{link}"
        response = self.session.get(full_url)

        return response.text

    @staticmethod
    def _get_soup(html: str) -> BeautifulSoup:
        """
        Create a BeautifulSoup object from HTML content.

        :param html: The HTML content.
        :return: A BeautifulSoup object.
        """

        return BeautifulSoup(html, "lxml")

    def _find_user_link_by_username(self, username: str) -> str | None:
        """
        Find the link to a user's page based on their username.

        :param username: The username of the user.
        :return: The relative URL of the user's page, or None if not found.
        """
        url = (
            f"abon_list.php?filter_selector0=logname&logname0_value={username}"
        )
        html = self._fetch_page(url)
        soup = self._get_soup(html)
        rows_data = soup.select("div.cursor_pointer")

        for row in rows_data:
            if username == row.select_one("div.center_div").text:
                link_element = row.select_one("div._number a")
                return link_element["href"] if link_element else None

        return None

    def _get_user_info(self, user_link: str) -> dict:
        """
        Extract user information from a user's page.

        :param user_link: The relative URL of the user's page.
        :return: A dictionary containing user information.
        """
        html = self._fetch_page(user_link)
        soup = self._get_soup(html)
        switch_cell = soup.select_one("a.paragraph")
        port_cell = soup.select_one("div.port_number")
        info = {
            "switch_link": switch_cell["href"] if switch_cell else None,
            "user_port": port_cell.get_text(strip=True)
            if port_cell
            else "no port",
        }
        return info

    def get_user_info(self, username: str) -> dict | None:
        """
        Retrieve user information based on their username.

        :param username: The username of the user.
        :return: A dictionary containing user information, or None if not found.
        """
        user_link = self._find_user_link_by_username(username)

        return self._get_user_info(user_link) if user_link else None

    def get_switch_info(self, username: str) -> dict | None:
        """
        Retrieve switch information associated with a user.

        :param username: The username of the user.
        :return: A dictionary containing switch information, or None if not found.
        """
        user_info = self.get_user_info(username)
        if user_info is None:
            return None

        user_link, port_number = user_info.values()
        html = self._fetch_page(user_link)
        soup = self._get_soup(html)

        device, address = soup.select_one("div.label_h2").text.split(" -> ")
        services_links = soup.select("div#block_left_id a")
        info = {"user_port": port_number, "device": device, "address": address}

        if len(services_links) > 1:
            info["telnet_link"] = services_links[1]["href"]
            info["access"] = soup.find("textarea").text.strip()

        return info


def main():
    main_login = env.str("LOGIN_USERSIDE")
    main_passwd = env.str("PASSWD_USERSIDE")
    main_url = env.str("URL_USERSIDE")

    with UsersideWebDataFetcher(
        main_url, main_login, main_passwd
    ) as data_fetcher:
        if data_fetcher.authenticate():
            print("Authentication successful")

            username = "nadiyabond"
            switch_data = data_fetcher.get_switch_info(username)
            print(switch_data)

            user_info = data_fetcher.get_user_info(username)
            print(user_info)

        else:
            print("Authentication failed")


if __name__ == "__main__":
    main()
