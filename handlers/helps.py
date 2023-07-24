from aiogram import types
import const_texts as ct


async def send_help(message: types.Message):
    """Send a help message"""
    msg = "Бот кожні 90 сек скануватиме nagios і якщо хост (адреса) лежить 5 хв і більше, то тільки тоді бот вважає, " \
          "що є проблема з цією адресою і надсилає повідомлення в чат, інакше буде ігнорувати всі адреси, які в стані " \
          "непрацюючих менше 5 хв"
    await message.answer(msg)
