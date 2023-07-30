from aiogram import executor

from apsched.jobs import start_scheduler
from handlers import start, helps
from handlers.credentials import (
    send_user_credentials,
    send_blank,
    send_seance,
    send_balance,
)
from handlers.critical_hosts import (
    send_critical_hosts_message,
    send_detailed_critical_hosts_message,
)
from loader import dp
from utils.db.data_process import DataBaseOperations
from utils.set_bot_commands import set_default_commands

# Register handlers for messages
dp.register_message_handler(start.send_welcome, commands=["start"])
dp.register_message_handler(helps.send_help, commands=["help"])
dp.register_message_handler(send_critical_hosts_message, commands=["nagios"])
dp.register_message_handler(send_user_credentials, commands=["abon"])
dp.register_callback_query_handler(send_blank, text_contains="blank")
dp.register_callback_query_handler(send_seance, text_contains="seance")
dp.register_callback_query_handler(send_balance, text_contains="balance")
dp.register_callback_query_handler(
    send_detailed_critical_hosts_message, text_contains="details"
)


async def on_start(dispatcher) -> None:
    """Start services for bot"""

    # Set commands for bot
    await set_default_commands(dispatcher)

    # Create table if it doesn't exist
    await DataBaseOperations().create_tables()

    # Start schedule
    await start_scheduler()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start)
