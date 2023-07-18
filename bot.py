from aiogram import types, executor
from aiogram.utils.markdown import text

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apsched.check_hosts import monitoring
import const_texts as ct
from loader import dp, env, is_silent
from utils.db.data_process import DataBaseOperations
from utils.nagios import GetCriticalHostNagios
from utils.log import logger
from utils.set_bot_commands import set_default_commands

# Create a scheduler
scheduler = AsyncIOScheduler(timezone="Europe/Kiev")


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(ct.start_text)


@dp.message_handler(commands=["nagios", "check"])
async def send_all_critical_hosts(message: types.Message):
    """Sends a notification with all critical hosts"""

    parser = GetCriticalHostNagios(
        url=env.str("URL_NAGIOS"),
        login=env.str("LOGIN_NAGIOS"),
        passwd=env.str("PASSWD_NAGIOS"),
    )

    if hosts := await parser.get_all_critical_hosts():
        msg = text(
            ct.all_down_hosts + f" ({len(hosts)})",
            "\n".join("🟥 • " + str(*i) for i in hosts),
            sep="\n\n",
        )
        await message.answer(text=msg)
        logger.info(
            "Critical hosts: %s. Sent to Telegram chat: %s", len(hosts),
            message.chat.id)
    else:
        await message.answer(text=ct.all_ok, disable_notification=is_silent())
        logger.warning("No critical hosts found. Data is empty.")


async def on_start(dispatcher):
    """Start services for bot"""

    # Set commands for bot
    await set_default_commands(dispatcher)

    # Create table if it doesn't exist
    await DataBaseOperations().create_tables()

    # Add tasks apscheduler
    scheduler.add_job(monitoring, "interval", seconds=10)

    # Start the scheduler
    scheduler.start()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start)
