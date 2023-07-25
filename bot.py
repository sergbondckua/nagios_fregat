from aiogram import executor

from apsched.check_hosts import monitoring
from handlers import start, helps, critical_hosts as ch
from loader import dp, scheduler
from utils.db.data_process import DataBaseOperations
from utils.set_bot_commands import set_default_commands


# Register handlers for messages
dp.register_message_handler(start.send_welcome, commands=["start"])
dp.register_message_handler(helps.send_help, commands=["help"])
dp.register_message_handler(ch.send_critical_hosts_message, commands=["nagios"])
dp.register_callback_query_handler(
    ch.send_detailed_critical_hosts_message, text_contains="details"
)


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
