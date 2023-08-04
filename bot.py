from aiogram import executor

from loader import dp
from utils.db.data_process import DataBaseOperations
from utils.set_bot_commands import set_default_commands
from apsched.jobs import start_scheduler
from handlers import start, helps
from handlers.critical_hosts import (
    send_critical_hosts_message,
    send_detailed_critical_hosts_message,
)
from handlers.credentials import (
    send_blank,
    send_session,
    send_balance,
    close,
    process_users_query,
    get_user_profile_credentials,
)

# Register handlers for messages
dp.register_message_handler(start.send_welcome, commands=["start"])
dp.register_message_handler(helps.send_help, commands=["help"])
dp.register_message_handler(send_critical_hosts_message, commands=["nagios"])
dp.register_message_handler(process_users_query, commands=["abon"])

# Register callback handlers
dp.register_callback_query_handler(send_blank, text_contains="blank")
dp.register_callback_query_handler(send_session, text_contains="session")
dp.register_callback_query_handler(send_balance, text_contains="balance")
dp.register_callback_query_handler(close, text_contains="close")
dp.register_callback_query_handler(
    get_user_profile_credentials, text_contains="profile"
)
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
