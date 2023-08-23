from __future__ import annotations
from aiogram import types
import const_texts as ct
from loader import env
from utils.api_userside.api import ApiUsersideData
from utils.db.data_process import DataBaseOperations
from utils.keyboards import make_inline_keyboard
from utils.misc import is_user_member
from utils.telnet_switch import TelnetSwitch


async def get_task_details(task_id: str) -> dict:
    """
    Retrieve task details from the API based on the task ID.
    """
    api = ApiUsersideData()
    task_api = await api.get_task(task_id)
    return task_api.get("Data")


async def get_customer_details(customer_id: str) -> dict:
    """
    Retrieve customer details from the API based on the customer ID.
    """
    api = ApiUsersideData()
    customer_api = await api.get_customer(customer_id)
    return customer_api.get("Data")


async def assign_task(message: types.Message):
    """
    Handle the assignment of a task to users or groups.
    """
    task_id = message.get_args().strip()
    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_name = (
        message.chat.title
        if message.chat.type != "private"
        else message.from_user.full_name
    )

    if not task_id:
        await message.answer(ct.correct_abon_command)
        return

    await message.answer_chat_action(action=types.ChatActions.TYPING)

    task_data = await get_task_details(task_id)
    task_info = {
        "num": task_data["id"],
        "address": task_data["address"]["text"],
        "type": task_data["type"]["name"],
    }

    users = await get_relevant_users(user_id, chat_id)
    buttons = await create_assignment_buttons(
        users, chat_name, chat_id, task_id
    )

    keyboard = await make_inline_keyboard(*sum(buttons, ()))
    msg = ct.assign_task_msg.format(
        task_info["num"], task_info["type"], task_info["address"]
    )

    await message.answer(msg, reply_markup=keyboard)


async def get_relevant_users(user_id: str, chat_id: str) -> list[dict]:
    users = await DataBaseOperations().get_users_profile_from_db()
    relevant_users = [
        user
        for user in users
        if user["user_id"] != user_id
        and (
            await is_user_member(chat_id, user["user_id"])
            or await is_user_member(env.int("CHAT_SUPPORT_ID"), user["user_id"])
        )
    ]
    return relevant_users


async def create_assignment_buttons(
    users: list[dict], chat_name: str, chat_id: int, task_id: str
) -> list[tuple[str, str]]:
    user_buttons = [
        (user["full_name"], f"send_to__{user['user_id']}__{task_id}")
        for user in users
    ]

    assignment_buttons = [
        *user_buttons,
        (chat_name, f"send_to__{chat_id}__{task_id}"),
        (ct.btn_close, "close"),
    ]
    return assignment_buttons


async def send_task(call: types.CallbackQuery):
    await call.message.answer_chat_action(action=types.ChatActions.TYPING)
    user_id, task_id = call.data.split("__")[1:]

    # Retrieve task details
    task_data = await get_task_details(task_id)
    customer_id = task_data["customer"]["id"]
    customer_data = await get_customer_details(customer_id)
    print(task_data, customer_data, sep="\n")

    msg = ct.send_task_msg.format(
        task_data["id"],
        task_data["type"]["name"],
        customer_data["full_name"] if customer_data else None,
        task_data.get("customer").get("login"),
        customer_data["phone"][1]["number"].replace("-", "")
        if customer_data
        else None,
        task_data["address"]["text"],
        await TelnetSwitch.replace_br_nbsp(task_data["description"]),
    )

    await call.bot.send_message(user_id, msg)
    await call.message.edit_text(ct.sent_success.format(task_id, user_id))
