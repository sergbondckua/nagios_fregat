import asyncio
import logging

from aiogram import Bot, types
from aiogram.utils.markdown import text, hbold, quote_html
from environs import Env

import const_texts as ct
from nagios import GetCriticalHostNagios

logging.basicConfig(
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-4s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)

# Read environment variables
env = Env()
env.read_env()


class NagiosTelegramNotifier:
    """Send a notification to the telegram"""

    def __init__(self, chat_id):
        self.bot = Bot(
            token=env.str("BOT_TOKEN"),
            parse_mode=types.ParseMode.HTML,
            disable_web_page_preview=False,
        )
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)

    async def send_checked_hosts_list(self, hosts: list) -> None:
        """Send a list of checked"""

        if hosts:
            msg = text(
                ct.changed_hosts_status, "\n".join(hosts),
                text(
                    "----", f"<a href='{ct.url_nagios}'>Nagios</a> | /nagios",
                    sep="\n",
                ),
                sep="\n\n",
            )
            await self.bot.send_message(chat_id=self.chat_id, text=msg)
        else:
            self.logger.info("The current status of the hosts has not changed")

    async def send_critical_hosts_notification(self, hosts) -> None:
        """Sends a notification with all critical hosts"""

        if hosts:
            msg = text(
                ct.all_down_hosts,
                "\n".join("🟥 " + str(*i) for i in hosts),
                sep="\n\n",
            )
            await self.bot.send_message(chat_id=self.chat_id, text=msg)
            self.logger.info(
                "Critical hosts: %s. Sent to Telegram chat: %s", len(hosts),
                self.chat_id)
        else:
            await self.bot.send_message(
                chat_id=self.chat_id, text="It's OK! Not found problems")
            self.logger.warning("No critical hosts found. Data is empty.")


async def main():
    parser = GetCriticalHostNagios(
        login=env.str("LOGIN_NAGIOS"), passwd=env.str("PASSWD_NAGIOS"))
    hosts = await parser.get_all_critical_hosts()
    sender = NagiosTelegramNotifier(chat_id=env.int("CHAT_DEV_ID"))
    await sender.send_critical_hosts_notification(hosts)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
