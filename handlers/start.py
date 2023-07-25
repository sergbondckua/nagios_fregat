from aiogram import types
import const_texts as ct


async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    bot_name = (await message.bot.get_me()).first_name
    await message.answer(ct.start_text % bot_name)
