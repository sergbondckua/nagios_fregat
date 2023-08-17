import requests
from bs4 import BeautifulSoup


class UsersideWebDataFetcher:
    """
    A class for fetching user and switch information from a web-based service.

    Attributes:
        base_url (str): The base URL of the web service.
        session (requests.Session): A session object for making HTTP requests.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def authenticate(self, username, password):
        login_url = f"{self.base_url}/adminlogin.php"
        payload = {"us_oper_login": username, "us_oper_pass": password}
        response = self.session.post(login_url, data=payload)
        return "login_page_alert" not in response.text

    def _fetch_page(self, link):
        full_url = f"{self.base_url}/oper/{link}"
        response = self.session.get(full_url)
        return response.text

    def find_user_link_by_username(self, username):
        url = (
            f"abon_list.php?filter_selector0=logname&logname0_value={username}"
        )
        html = self._fetch_page(url)
        soup = BeautifulSoup(html, "lxml")
        link_element = soup.select_one("div._number a")
        link = link_element["href"] if link_element else None

        return link

    def get_user_info(self, username):
        user_link = self.find_user_link_by_username(username)
        if user_link:
            html = self._fetch_page(user_link)
            soup = BeautifulSoup(html, "lxml")
            switch_cell = soup.select_one("a.paragraph")
            switch_link = switch_cell["href"] if switch_cell else None
            port_cell = soup.select_one("div.port_number")
            port_number = (
                port_cell.get_text(strip=True) if port_cell else "no port"
            )
            return port_number, switch_link
        return None

    def get_switch_info(self, username):
        try:
            port_number, user_link = self.get_user_info(username)
        except TypeError as e:
            print(str(e))
            return None

        html = self._fetch_page(user_link)
        soup = BeautifulSoup(html, "lxml")
        services_links = soup.select("div#block_left_id a")
        if len(services_links) > 1:
            telnet_link = services_links[1]["href"]
            access = soup.find("textarea").text.strip()
            return access, telnet_link, port_number
        return None


def main():
    # Replace with your actual credentials
    main_login = "---"
    main_passwd = "---"
    main_url = "000"

    with UsersideWebDataFetcher(main_url) as data_fetcher:
        if data_fetcher.authenticate(main_login, main_passwd):
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
