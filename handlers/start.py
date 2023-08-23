from aiogram import types
import const_texts as ct
from utils.db.data_process import DataBaseOperations


async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """

    # Initialize the database operations
    db = DataBaseOperations()
    bot_name = (await message.bot.get_me()).first_name
    await db.save_user_profile_to_db(message.from_user)  # Save the user profile
    await message.answer(ct.start_text.format(bot_name))
