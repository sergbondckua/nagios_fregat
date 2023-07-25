from aiogram import types
import const_texts as ct


async def send_help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    await message.answer(ct.help_text)
