import requests
from bs4 import BeautifulSoup


class UsersideWebDataFetcher:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def authenticate(self, username, password):
        login_url = f"{self.base_url}/adminlogin.php"
        payload = {"us_oper_login": username, "us_oper_pass": password}
        response = self.session.post(login_url, data=payload)
        return "login_page_alert" not in response.text

    def fetch_page(self, link):
        full_url = f"{self.base_url}/oper/{link}"
        response = self.session.get(full_url)
        return response.text

    def find_user_link_by_username(self, username):
        url = (
            f"abon_list.php?filter_selector0=logname&logname0_value={username}"
        )
        html = self.fetch_page(url)
        soup = BeautifulSoup(html, "lxml")
        link = soup.select_one("div._number a")["href"]

        return link

    def get_user_info(self, username):
        user_link = self.find_user_link_by_username(username)
        html = self.fetch_page(user_link)
        soup = BeautifulSoup(html, "lxml")
        switch_link = soup.select_one("a.paragraph")["href"]
        port_cell = soup.select_one("div.port_number")
        port_number = port_cell.get_text(strip=True) if port_cell else "no port"
        return port_number, switch_link

    def get_switch_info(self, username):
        user_link = self.get_user_info(username)[1]
        html = self.fetch_page(user_link)
        soup = BeautifulSoup(html, "lxml")
        telnet_link = soup.select("div#block_left_id a")[1]["href"]
        access = soup.find("textarea").text.strip()

        return access, telnet_link


if __name__ == "__main__":
    # Replace with your actual credentials
    username = "***"
    password = "***"

    url = "http://00.00.00.00"

    data_fetcher = UsersideWebDataFetcher(url)

    if data_fetcher.authenticate(username, password):
        print("Authentication successful")
        data = data_fetcher.get_switch_info("bb")
        ui = data_fetcher.get_user_info("aaa")
        print(data, ui)
        # Add your parsing logic using the BeautifulSoup parsed data

    else:
        print("Authentication failed")
