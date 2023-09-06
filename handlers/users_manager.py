from aiogram import types

from utils.db.data_process import DataBaseOperations


async def get_all_users(message: types.Message):
    """Sends a message to all users in the database"""

    users = await DataBaseOperations().get_users_from_db()
    msg = "\n".join(
        [
            ", ".join([str(value) for value in dict(item).values()])
            for item in users
        ]
    )

    await message.answer(msg)
