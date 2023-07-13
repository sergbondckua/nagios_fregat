import logging

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# Enable logging
logging.basicConfig(format="%(levelname)s - %(message)s",
                    level=logging.INFO)


class GetCriticalHostNagios:
    """Parser for critical hosts from Nagios"""

    _URL = "http://193.108.248.20/nagios/cgi-bin/status.cgi"

    def __init__(self, login, passwd):
        """
        Initializes the GetCriticalHostNagios instance.

        Args:
            login (str): Nagios login.
            passwd (str): Nagios password.
        """
        self.session = requests.Session()
        self.auth = (login, passwd)
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Content-Type": "text/html; charset=UTF-8",
            "User-Agent": UserAgent().random
        }
        self.params = {
            "hostgroup": "all",
            "style": "detail",
            "servicestatustypes": 16,
            "hoststatustypes": 15
        }

    def get_all_hosts(self):
        """
        Retrieves a list of critical hosts_name from Nagios.

        Returns:
            list: List of critical hosts_name.
        """

        response = self.session.get(
            url=self._URL,
            params=self.params,
            auth=self.auth,
            headers=self.headers,
            timeout=3,
        )
        if response.status_code != 200:
            self.logger.error("Error")
            return
        soup = BeautifulSoup(response.content, "lxml")
        hosts_name = soup.find_all(
            "td",
            {"class": "statusBGCRITICAL", "valign": "center", "align": "left"}
        )

        return [self._get_one_host(host) for host in hosts_name]

    @staticmethod
    def _get_one_host(host):
        """
        Extracts the host name from a BeautifulSoup object.

        Args:
            host (BeautifulSoup): BeautifulSoup object representing a host.

        Returns:
            str: Host name.
        """
        return host.find("a").text.strip()


if __name__ == "__main__":
    res = GetCriticalHostNagios(login="wew", passwd="wewe")
    print(res.get_all_hosts(), sep="\n")
