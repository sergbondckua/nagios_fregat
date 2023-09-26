from aiogram import types

import const_texts as ct
from handlers.task_manager import get_full_name
from utils.db.data_process import DataBaseOperations
from utils.keyboards import make_inline_keyboard
from utils.misc import require_group_membership
from const_texts import btn_close


@require_group_membership()
async def get_all_users(message: types.Message):
    """Sends a message to all users in the database"""
    query_users = await DataBaseOperations().get_users_from_db()
    users = query_users.fetchall()
    buttons = [
        (user["full_name"], f"bot_user__{user['user_id']}") for user in users
    ] + [(btn_close, "close")]
    keyboard = await make_inline_keyboard(*sum(buttons, ()))

    text = "\n".join(
        [
            ", ".join([str(value) for value in dict(item).values()])
            for item in users
        ]
    )
    msg = text if text else ct.not_found_users
    await message.answer(msg, reply_markup=keyboard)


async def get_simple_user_menu(call: types.CallbackQuery):
    """Get the user menu and display user information."""

    user_id = call.data.split("__")[1]
    db = DataBaseOperations()  # Initialize the database operations
    user = dict(await db.get_simple_user(user_id))
    full_name = user.get("full_name")
    duty = bool(user.get("duty"))
    is_duty = bool(user.get("is_duty"))
    staff = bool(user.get("staff"))
    buttons = generate_buttons(user_id, staff, duty, is_duty=is_duty)
    keyboard = await make_inline_keyboard(*buttons)
    msg = ct.user_menu_text.format(
        full_name,
        "✔️" if staff else "➖",
        "✔️" if duty else "➖",
        "✔️" if is_duty else "➖",
    )
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
    is_duty = bool(data.get("is_duty"))
    buttons = generate_buttons(user_id, staff=staff, duty=duty, is_duty=is_duty)
    keyboard = await make_inline_keyboard(*buttons)
    full_name = await get_full_name(user_id)
    msg = ct.user_menu_text.format(
        full_name,
        "✔️" if staff else "➖",
        "✔️" if duty else "➖",
        "✔️" if is_duty else "➖",
    )

    await call.message.edit_text(msg)
    await call.message.edit_reply_markup(reply_markup=keyboard)


async def change_user_day_off_duty(call: types.CallbackQuery):
    """Set or unset the user day off duty for the database"""
    await change_user_data(call, "duty")


async def change_user_staff(call: types.CallbackQuery):
    """Set or unset the user staff for the database"""
    await change_user_data(call, "staff")


async def delete_user(call: types.CallbackQuery):
    """Delete the user from the database"""

    user_id = call.data.split("__")[-1]
    db = DataBaseOperations()  # Initialize the database operations
    await db.delete_user_profile_from_db(user_id)
    await call.message.delete()
    await call.message.answer(f"Delete {user_id} user profile")


def generate_buttons(user_id: str, staff: bool, duty: bool, is_duty: bool) -> tuple:
    """Generate buttons for the user menu."""

    # Determine the is_duty button text and call based on duty and is_duty values
    if duty:
        is_duty_name = "Черговий" if not is_duty else "Не черговий"
        is_duty_call = f"change_is_duty__{user_id}_1" if not is_duty else f"change_is_duty__{user_id}_0"
    else:
        is_duty_name, is_duty_call = "None", "None"

    # Create a list of buttons with their respective texts and calls
    buttons = [
        ct.btn_implementer if not staff else ct.btn_not_implementer,
        f"change_mounter__{user_id}_1" if not staff else f"change_mounter__{user_id}_0",
        ct.btn_duty_man if not duty else ct.btn_not_duty_man,
        f"change_duty__{user_id}_1" if not duty else f"change_duty__{user_id}_0",
        is_duty_name,
        is_duty_call,
        ct.btn_delete_user,
        f"delete__{user_id}",
        btn_close,
        "close",
    ]

    # Remove "None" entries if present
    buttons = [btn for btn in buttons if btn not in ["None", "None"]]

    return tuple(buttons)
