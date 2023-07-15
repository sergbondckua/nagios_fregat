import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from environs import Env

from nagios import GetCriticalHostNagios

logging.basicConfig(
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-4s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

env = Env()
env.read_env()

bot = Bot(
    token=env.str("BOT_TOKEN"),
    parse_mode=types.ParseMode.HTML,
)
dp = Dispatcher(bot)


async def send_message_to_telegram_chat(chat_id) -> None:
    """Sends all critical hosts in a Telegram chat message"""

    parser = GetCriticalHostNagios(
        login=env.str("LOGIN_NAGIOS"), passwd=env.str("PASSWD_NAGIOS"))
    hosts = await parser.get_all_hosts()
    msg = "\n".join(f"🔴 {str(*host)}" for host in hosts)

    if hosts:
        logger.info(
            "Critical hosts: %s. Sent to Telegram chat: %s",
            len(hosts),
            chat_id,
        )
        await bot.send_message(chat_id=chat_id, text=msg)
    else:
        logger.warning("Not found data. Data is empty.")


async def send_checked_hosts(hosts: list) -> None:
    """Send a list of checked"""


async def main():
    await send_message_to_telegram_chat(chat_id=env.int("CHAT_DEV_ID"))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
