from aiogram import types, executor
from aiogram.types import CallbackQuery

from apsched.check_hosts import monitoring
import const_texts as ct
from loader import dp, env, is_night_time, scheduler
from utils.db.data_process import DataBaseOperations
from utils.keyboards import make_inline_keyboard
from utils.nagios import GetCriticalHostNagios
from utils.log import logger
from utils.set_bot_commands import set_default_commands


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    bot_name = (await message.bot.get_me()).first_name
    await message.answer(ct.start_text % bot_name)


@dp.message_handler(commands=["nagios", "check"])
async def send_all_critical_hosts(message: types.Message):
    """Sends a notification with all critical hosts"""

    parser = GetCriticalHostNagios(
        url=env.str("URL_NAGIOS"),
        login=env.str("LOGIN_NAGIOS"),
        passwd=env.str("PASSWD_NAGIOS"),
    )

    if hosts := await parser.get_all_critical_hosts():

        # Convert the list of changed hosts to a formatted string
        hosts_str = "\n".join("🟥 • " + str(i[0]) for i in hosts)

        keyboard = await make_inline_keyboard(
            "🕵 Детально", "details", row_width=1)

        await message.answer(
            text=ct.all_down_hosts % (len(hosts), hosts_str),
            disable_notification=is_night_time(),
            reply_markup=keyboard,
        )
        logger.info(
            "Critical hosts: %s. Sent to Telegram chat: %s", len(hosts),
            message.chat.id)
    else:
        await message.answer(
            text=ct.all_ok,
            disable_notification=is_night_time(),
        )
        logger.warning("No critical hosts found. Data is empty.")


@dp.callback_query_handler(text_contains="details")
async def send_all_critical_hosts_with_down_time(call: CallbackQuery):
    """Sends all the details of all hosts that are down."""

    await call.message.edit_reply_markup()
    await call.message.delete()

    parser = GetCriticalHostNagios(
        url=env.str("URL_NAGIOS"),
        login=env.str("LOGIN_NAGIOS"),
        passwd=env.str("PASSWD_NAGIOS"),
    )

    if hosts := await parser.get_all_critical_hosts():

        # Convert the list of changed hosts to a formatted string
        hosts_str = "\n".join(
            "🔻 <b>|-- " + str(i[0]) + "</b>\n       <b>|--</b>  " + str(i[1]) + "\n"
            for i in hosts)

        await call.message.answer(
            text=ct.all_down_hosts % (len(hosts), hosts_str),
        )
        logger.info(
            "Critical hosts: %s. Sent to Telegram chat: %s",
            len(hosts), call.message.chat.id)


async def on_start(dispatcher):
    """Start services for bot"""

    # Set commands for bot
    await set_default_commands(dispatcher)

    # Create table if it doesn't exist
    await DataBaseOperations().create_tables()

    # Add tasks apscheduler
    scheduler.add_job(monitoring, "interval", seconds=90)

    # Start the scheduler
    scheduler.start()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start)
