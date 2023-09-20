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


async def set_user_day_off_duty(message: types.Message):
    """Set the user day off duty for the database"""

    user_id = message.get_args().split(" ")[0].strip()
    db = DataBaseOperations()  # Initialize the database operations

    if user_id.isdigit():
        await db.set_duty_user_to_db(user_id=user_id, duty=False)
        await message.answer("Set user day off duty " + user_id)
    else:
        await message.answer("Not set user day off duty")
