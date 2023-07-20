from datetime import datetime, time
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from environs import Env

# Read environment variables
env = Env()
env.read_env()

# Initialize bot and dispatcher
bot = Bot(token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Create a scheduler
scheduler = AsyncIOScheduler(timezone=env.str("TZ"))


def is_night_time():
    """
    Checks if the current time is within the night hours.

    Returns:
        bool: True if the current time is during the night, False otherwise.
    """

    now = datetime.now(tz=timezone(env.str("TZ"))).time()
    start_night_time = time(22, 0)
    end_night_time = time(7, 0)

    return start_night_time <= now or now <= end_night_time
