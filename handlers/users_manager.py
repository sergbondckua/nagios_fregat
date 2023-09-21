import asyncio

from aiogram import types

import const_texts as ct
from utils.db.data_process import DataBaseOperations
from utils.keyboards import make_inline_keyboard


async def get_all_users(message: types.Message = None):
    """Sends a message to all users in the database"""

    users = await DataBaseOperations().get_users_from_db()

    buttons = [
        (user["full_name"], f"bot_user__{user['user_id']}") for user in users
    ] + [(ct.btn_close, "close")]
    keyboard = await make_inline_keyboard(*sum(buttons, ()))
    print(buttons)

    msg = "\n".join(
        [
            ", ".join([str(value) for value in dict(item).values()])
            for item in users
        ]
    )

    await message.answer(msg, reply_markup=keyboard)


async def get_simple_user(call: types.CallbackQuery):
    """TODO: implement"""
    user_id = call.data.split("__")[1]

    buttons = (
        "Set Mounter",
        f"set_mounter__{user_id}",
        "Unset Mounter",
        f"unset_mounter__{user_id}",
        "Set Duty",
        f"set_duty__{user_id}",
        "Unset Duty",
        f"unset_duty__{user_id}",
        "Delete",
        f"delete__{user_id}",
        ct.btn_close,
        "close"
    )

    keyboard = await make_inline_keyboard(*buttons, row_width=2)
    await call.message.answer(user_id, reply_markup=keyboard)


async def set_user_day_off_duty(message: types.Message):
    """Set the user day off duty for the database"""

    user_id = message.get_args().split(" ")[0].strip()
    db = DataBaseOperations()  # Initialize the database operations

    if user_id.isdigit():
        await db.update_user_to_db(user_id=user_id, duty=True)
        await message.answer("Set user day off duty " + user_id)
    else:
        await message.answer("Not set user day off duty")


if __name__ == "__main__":
    asyncio.run(get_all_users())
