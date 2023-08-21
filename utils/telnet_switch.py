import asyncio
import re
import urllib.parse
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from bs4 import BeautifulSoup
from loader import env


class TelnetSwitch:
    """A class for interacting with a Telnet switch."""

    def __init__(self, url: str, port: int):
        """
        Initialize the TelnetSwitch instance.

        Args:
            url (str): The base URL of the Telnet switch.
            port (int): The port number.

        """
        self.url = url
        self.port = port
        self.timeout = ClientTimeout(total=20)
        self.connector = TCPConnector(ssl=False, limit_per_host=10)
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.session = ClientSession(
            timeout=self.timeout,
            connector=self.connector,
            headers=self.headers,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def _execute_action(self, action: str) -> str:
        """Execute a Telnet switch action."""

        payload = await self._get_payload(action=action)
        return await self._post_data(payload=payload)

    async def _fetch_data(self, url: str) -> str:
        """Fetch data from the specified URL."""

        async with self.session.get(url) as response:
            return await response.text()

    async def _post_data(self, payload: str) -> str:
        """
        Post data to the Telnet switch.

        Args:
            payload (str): The payload data to post.

        Returns:
            str: The response text from the post request.

        """
        url = f"{env.str('URL_USERSIDE').rstrip('/')}:8000/telnet"
        async with self.session.post(url, data=payload) as response:
            return await response.text()

    async def _get_payload(self, action: str) -> str:
        """
        Get the payload data for a Telnet switch action.

        Args:
            action (str): The action to create payload for.

        Returns:
            str: The formatted payload data.

        """
        html = await self._fetch_data(self.url)
        soup = BeautifulSoup(html, "lxml")
        form = soup.select_one("form")
        payload = {
            "ip": form.select_one("input#ip").get("value"),
            "model": form.select_one("input#model").get("value"),
            "cmd": urllib.parse.quote(action, encoding="cp1251"),
            "port": self.port,
            "vid": None,
            "mac": None,
        }
        payload_format = "&".join(
            f"{key}={value}" for key, value in payload.items()
        )
        return payload_format

    @staticmethod
    async def extract_mac_addresses(text: str) -> str:
        """Extracts MAC addresses from the provided text."""

        mac_pattern = r"([0-9A-Fa-f]{2}(?:[:-][0-9A-Fa-f]{2}){5})"
        mac_addresses = re.findall(mac_pattern, text)
        mac_str = (
            ",".join(mac_addresses)
            if mac_addresses
            else "No MAC addresses found"
        )
        return mac_str

    @staticmethod
    async def replace_br_nbsp(text):
        """Replace '<br>' tags with newline characters and '&nbsp;'."""

        replaced_br = text.replace("<br>", "\n")
        final_text = replaced_br.replace("&nbsp;", " ")
        return final_text

    async def show_mac(self) -> str:
        """Show MAC addresses on the Telnet switch."""

        mac = await self._execute_action(action="show mac")
        return await self.extract_mac_addresses(mac)

    async def show_errors(self) -> str:
        """Show port ERRORS on the Telnet switch."""

        cmd_errors = await self._execute_action(action="show errors")
        cleaned_errors = await self.replace_br_nbsp(cmd_errors)
        errors = "".join(
            line.strip()
            for line in cleaned_errors.splitlines()
            if "Errors" in line
        )
        return errors if errors else "Errors: 0"

    async def cable_test(self) -> str:
        """Perform cable test on the Telnet switch."""

        test = await self._execute_action(action="cable test")
        return await self.replace_br_nbsp(test)

    async def port_enable(self) -> str:
        """Enable the port on the switch."""
        return await self._execute_action(action="port enable")

    async def port_disable(self) -> str:
        """Disable the port on the switch."""
        return await self._execute_action(action="port disable")


async def main():
    url = "http://193.108.248.20:8000/172.24.61.189/D-Link%20DES-3200-26/C1"
    port = 25
    async with TelnetSwitch(url=url, port=port) as send_telnet:
        res = await send_telnet.cable_test()
        print(res)


if __name__ == "__main__":
    asyncio.run(main())
