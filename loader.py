from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from environs import Env

from nagios import GetCriticalHostNagios
from send import NagiosTelegramNotifier

# Read environment variables
env = Env()
env.read_env()

# Initialize bot and dispatcher
bot = Bot(token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(commands=['nagios', 'check'])
async def send_all_critical_hosts(_: types.Message):
    """Send all critical hosts to the Network Cherkasy city"""

    parser = GetCriticalHostNagios(
        login=env.str("LOGIN_NAGIOS"), passwd=env.str("PASSWD_NAGIOS"))
    hosts = await parser.get_all_critical_hosts()
    sender = NagiosTelegramNotifier(chat_id=env.int("CHAT_DEV_ID"))
    await sender.send_critical_hosts_notification(hosts)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
