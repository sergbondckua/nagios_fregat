from aiogram import executor

from apsched.jobs import start_scheduler
from handlers import start, helps, critical_hosts as ch
from loader import dp
from utils.db.data_process import DataBaseOperations
from utils.set_bot_commands import set_default_commands

# Register handlers for messages
dp.register_message_handler(start.send_welcome, commands=["start"])
dp.register_message_handler(helps.send_help, commands=["help"])
dp.register_message_handler(ch.send_critical_hosts_message, commands=["nagios"])
dp.register_callback_query_handler(
    ch.send_detailed_critical_hosts_message, text_contains="details"
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
