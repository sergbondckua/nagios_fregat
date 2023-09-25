import asyncio
from aiogram import types

from handlers.task_manager import get_full_name
from utils.db.data_process import DataBaseOperations
from utils.keyboards import make_inline_keyboard
from utils.misc import require_group_membership
from const_texts import btn_close


@require_group_membership()
async def get_all_users(message: types.Message):
    """Sends a message to all users in the database"""
    users = await DataBaseOperations().get_users_from_db()
    buttons = [
        (user["full_name"], f"bot_user__{user['user_id']}") for user in users
    ] + [(btn_close, "close")]
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
    """Get the user menu and display user information."""

    user_id = call.data.split("__")[1]
    db = DataBaseOperations()  # Initialize the database operations
    user = dict(await db.get_simple_user(user_id))
    full_name = user.get("full_name")
    duty = bool(user.get("duty"))
    staff = bool(user.get("staff"))
    msg = f"{full_name}\nПерсонал: {staff}\nЧергування: {duty}"
    buttons = generate_buttons(user_id, staff, duty)
    keyboard = await make_inline_keyboard(*buttons)
    await call.message.answer(msg, reply_markup=keyboard)


async def change_user_data(call: types.CallbackQuery, attribute_name: str):
    """Set or unset the user attribute for the database"""

    user_id, attribute_value = call.data.split("__")[-1].split("_")
    db = DataBaseOperations()  # Initialize the database operations
    await db.update_user_to_db(
        user_id=user_id, **{attribute_name: attribute_value}
    )

    data = dict(await db.get_simple_user(user_id))
    staff = bool(data.get("staff"))
    duty = bool(data.get("duty"))
    buttons = generate_buttons(user_id, staff=staff, duty=duty)
    keyboard = await make_inline_keyboard(*buttons)
    full_name = await get_full_name(user_id)
    msg = f"{full_name}\nПерсонал: {'✔️' if staff else '➖'}\nЧергування: {duty}"

    await call.message.edit_text(msg)
    await call.message.edit_reply_markup(reply_markup=keyboard)
    # await call.message.answer(
    #     f"Change {full_name} user {attribute_name} to {bool(data.get(attribute_name))}"
    # )


async def change_user_day_off_duty(call: types.CallbackQuery):
    """Set or unset the user day off duty for the database"""
    await change_user_data(call, "duty")


async def change_user_staff(call: types.CallbackQuery):
    """Set or unset the user staff for the database"""
    await change_user_data(call, "staff")


def generate_buttons(user_id: str, staff: bool, duty: bool) -> tuple:
    """Generate buttons for the user menu."""
    return (
        "✔️ Set Mounter" if not staff else "➖ Unset Mounter",
        f"change_mounter__{user_id}_1"
        if not staff
        else f"change_mounter__{user_id}_0",
        # duty
        "✔️ Set Duty" if not duty else "➖ Unset Duty",
        f"change_duty__{user_id}_1"
        if not duty
        else f"change_duty__{user_id}_0",
        # delete
        "❌ Delete",
        f"delete__{user_id}",
        btn_close,
        "close",
    )


if __name__ == "__main__":
    asyncio.run(get_simple_user_menu("5278577154"))
