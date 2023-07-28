from aiogram import executor

from apsched.check_hosts import monitoring
from apsched.storm_warning import notice_of_possible_thunderstorms
from handlers import start, helps, critical_hosts as ch
from loader import dp, scheduler, env
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


async def start_scheduler() -> None:
    """Start scheduler and add tasks apscheduler"""

    scheduler.add_job(monitoring, "interval", seconds=90)

    if env.bool("IS_REPORT_STORM"):
        scheduler.add_job(
            func=notice_of_possible_thunderstorms,
            trigger="cron",
            minute=0,
            hour=8,
            month="3-11",
            day_of_week="mon, wed, fri",
        )

    # Start the scheduler
    scheduler.start()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start)
