from aiogram import executor

from apsched.jobs import start_scheduler
from handlers.task_manager import task_assignment
from loader import dp
from utils.db.data_process import DataBaseOperations
from utils.set_bot_commands import set_default_commands

# Import individual handler functions
from handlers import start, helps
from handlers.critical_hosts import (
    send_critical_hosts,
    send_details_critical_hosts,
)
from handlers.credentials import (
    close,
    display_user_profile_menu,
    process_users_query,
    send_balance,
    send_blank,
    send_session,
)
from handlers.usersider import (
    send_access_device,
    show_mac_port,
    telnet_menu,
    cable_test,
    show_errors_port,
)

# Register messages handlers
dp.register_message_handler(start.send_welcome, commands=["start"])
dp.register_message_handler(helps.send_help, commands=["help"])
dp.register_message_handler(send_critical_hosts, commands=["nagios"])
dp.register_message_handler(process_users_query, commands=["abon", "ab"])
dp.register_message_handler(task_assignment, commands=["num", "№", "#"])

# Register callback handlers
dp.register_callback_query_handler(send_blank, text_contains="blank")
dp.register_callback_query_handler(send_session, text_contains="session")
dp.register_callback_query_handler(send_balance, text_contains="balance")
dp.register_callback_query_handler(send_access_device, text_contains="access")
dp.register_callback_query_handler(telnet_menu, text_contains="telnet")
dp.register_callback_query_handler(show_mac_port, text_contains="show_mac")
dp.register_callback_query_handler(cable_test, text_contains="cable_test")
dp.register_callback_query_handler(close, text_contains="close")
dp.register_callback_query_handler(
    show_errors_port, text_contains="show_errors"
)
dp.register_callback_query_handler(
    display_user_profile_menu, text_contains="profile"
)
dp.register_callback_query_handler(
    send_details_critical_hosts, text_contains="details"
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
