from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from environs import Env

from apsched.check_hosts import monitoring
from data_process import DataBaseOperations
from nagios import GetCriticalHostNagios
from send import NagiosTelegramNotifier
from utils.set_bot_commands import set_default_commands
import const_texts as ct

# Read environment variables
env = Env()
env.read_env()

# Initialize bot and dispatcher
bot = Bot(token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Create a scheduler
scheduler = AsyncIOScheduler(timezone="Europe/Kiev")


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(ct.start_text)


@dp.message_handler(commands=["nagios", "check"])
async def send_all_critical_hosts(_: types.Message):
    """Send all critical hosts to the Network Cherkasy city"""

    parser = GetCriticalHostNagios(
        login=env.str("LOGIN_NAGIOS"), passwd=env.str("PASSWD_NAGIOS")
    )
    hosts = await parser.get_all_critical_hosts()
    sender = NagiosTelegramNotifier(chat_id=env.int("CHAT_DEV_ID"))
    await sender.send_critical_hosts_notification(hosts)


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
