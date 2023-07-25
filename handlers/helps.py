from aiogram import types
import const_texts as ct


async def send_help(message: types.Message):
    """Send a help message"""
    await message.answer(ct.help_text)
