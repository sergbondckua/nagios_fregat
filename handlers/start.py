from aiogram import types
import const_texts as ct
from utils.db.data_process import DataBaseOperations


async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """

    arg = message.get_args()
    db = DataBaseOperations()  # Initialize the database operations
    bot_name = (await message.bot.get_me()).first_name

    # Save the user profile
    if arg == "mounter":
        await db.update_or_create_user_to_db(message.from_user, staff=True)
    elif arg == "delme":
        await db.delete_user_profile_from_db(message.from_user.id)
    else:
        await db.save_user_profile_to_db(message.from_user)

    await message.answer(ct.start_text.format(bot_name))
