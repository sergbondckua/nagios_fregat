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


async def get_simple_user_menu(call: types.CallbackQuery):
    """TODO: implement"""
    user_id = call.data.split("__")[1]
    db = DataBaseOperations()  # Initialize the database operations
    user = dict(await db.get_simple_user(user_id))
    full_name = user.get("full_name")
    duty = bool(user.get("duty"))
    staff = bool(user.get("staff"))
    msg = f"{full_name}\nЧергування: {duty}, Персонал: {staff}"

    buttons = generate_buttons(user_id, staff, duty)
    print(buttons)

    keyboard = await make_inline_keyboard(*buttons, row_width=1)
    await call.message.answer(msg, reply_markup=keyboard)


async def set_user_day_off_duty(message: types.Message):
    """Set the user day off duty for the database"""

    user_id = message.get_args().split(" ")[0].strip()
    db = DataBaseOperations()  # Initialize the database operations

    if user_id.isdigit():
        await db.update_user_to_db(user_id=user_id, duty=True)
        await message.answer("Set user day off duty " + user_id)
    else:
        await message.answer("Not set user day off duty")

def generate_buttons(user_id: str, staff: bool, duty: bool) -> tuple:
    """Generate buttons for the user menu."""
    return (
        "Set Mounter" if not staff else "Unset Mounter",
        f"set_mounter__{user_id}_{True}" if not staff else f"set_mounter__{user_id}_{False}",
        "Set Duty" if not duty else "Unset Duty",
        f"set_duty__{user_id}_{True}" if not duty else f"set_duty__{user_id}_{False}",
        "Delete",
        f"delete__{user_id}",
        ct.btn_close,
        "close",
    )


if __name__ == "__main__":
    asyncio.run(get_simple_user_menu("5278577154"))
