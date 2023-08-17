import requests
from bs4 import BeautifulSoup


class UsersideWebDataFetcher:
    """
    A class for fetching user and switch information from a web-based service.
    """

    def __init__(self, base_url, login, password):
        self.base_url = base_url
        self.username = login
        self.password = password
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def authenticate(self):
        login_url = f"{self.base_url}/adminlogin.php"
        payload = {
            "us_oper_login": self.username,
            "us_oper_pass": self.password,
        }
        response = self.session.post(login_url, data=payload)
        return "login_page_alert" not in response.text

    def _fetch_page(self, link):
        full_url = f"{self.base_url}/oper/{link}"
        response = self.session.get(full_url)
        return response.text

    @staticmethod
    def _get_soup(html):
        return BeautifulSoup(html, "lxml")

    def _find_user_link_by_username(self, username):
        url = (
            f"abon_list.php?filter_selector0=logname&logname0_value={username}"
        )
        html = self._fetch_page(url)
        soup = self._get_soup(html)
        link_element = soup.select_one("div._number a")
        link = link_element["href"] if link_element else None

        return link

    def get_user_info(self, username):
        user_link = self._find_user_link_by_username(username)
        if user_link:
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
        return None

    def get_switch_info(self, username):
        try:
            user_link, port_number = (
                item for item in self.get_user_info(username).values()
            )
        except TypeError as e:
            print(str(e))
            return None

        info = {"port": port_number}
        html = self._fetch_page(user_link)
        soup = self._get_soup(html)
        services_links = soup.select("div#block_left_id a")
        if len(services_links) > 1:
            info["telnet_link"] = services_links[1]["href"]
            info["access"] = soup.find("textarea").text.strip()
            return info
        return None


def main():
    # Replace with your actual credentials
    main_login = "---"
    main_passwd = "---"
    main_url = "000"

    with UsersideWebDataFetcher(
        main_url, main_login, main_passwd
    ) as data_fetcher:
        if data_fetcher.authenticate():
            print("Authentication successful")

            username = "test"
            switch_data = data_fetcher.get_switch_info(username)
            print(switch_data)

            user_info = data_fetcher.get_user_info(username)
            print(user_info)

        else:
            print("Authentication failed")


if __name__ == "__main__":
    main()
