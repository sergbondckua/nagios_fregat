from __future__ import annotations

import re

import aiogram
from aiogram import types
import const_texts as ct
from loader import bot, env
from utils.api_search_keys import CellSearchAPI
from utils.api_userside.api import ApiUsersideData
from utils.db.data_process import DataBaseOperations
from utils.keyboards import make_inline_keyboard
from utils.misc import (
    remove_html_tags,
    replacing_phone_numbers_in_text,
    require_group_membership,
    parse_address,
)


async def get_full_name(user_id: int) -> str:
    """Get the full name of a user using their user ID."""

    user = await bot.get_chat(user_id)
    full_name = user.full_name
    return full_name


async def get_task_details(task_id: str) -> dict:
    """Retrieve task details from the API based on the task ID."""

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


@require_group_membership(env.list("ALLOWED_CHAT_IDS"))
async def assign_task(message: types.Message):
    """
    Handle the assignment of a task to users or groups.
    """

    if message.get_args():
        task_id = message.get_args().strip()
    else:
        task_id = re.findall(r"#\d+", message.text)[0].lstrip("#")

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

    if task_data := await get_task_details(task_id):
        task_info = {
            "num": task_data["id"],
            "address": task_data["address"]["text"],
            "type": task_data["type"]["name"],
        }
    else:
        await message.answer(ct.not_found_task_id)
        return

    users = await get_relevant_users(user_id)
    buttons = await create_assignment_buttons(
        users, chat_name, chat_id, task_id
    )

    keyboard = await make_inline_keyboard(*sum(buttons, ()))
    msg = ct.assign_task_msg.format(
        task_info["num"], task_info["type"], task_info["address"]
    )

    await message.answer(msg, reply_markup=keyboard)


async def get_relevant_users(user_id: str) -> list[dict]:
    """Get relevant users"""

    users = await DataBaseOperations().get_users_from_db(**{"staff": True})
    relevant_users = [user for user in users if user["user_id"] != user_id]

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
    full_name = await get_full_name(user_id)
    task_data = await get_task_details(task_id)
    keyboard = await make_inline_keyboard(
        ct.btn_comment,
        f"add_comment__{task_id}",
        ct.btn_add_photo,
        f"attach__journal_{task_id}",
        ct.btn_close,
        "close",
        row_widths=[2, 1],
    )

    task_type_name = task_data["type"].get("name")
    customer_full_name = task_data["customer"].get("fullName")
    customer_login = task_data["customer"].get("login")
    login = f"/ab chk_{customer_login}" if customer_login else "➖"
    address_text = task_data["address"].get("text")
    description = await remove_html_tags(task_data["description"])
    text = await replacing_phone_numbers_in_text(description)
    parse = parse_address(address_text)

    if parse is not None:
        street_name = parse.get("street")
        street_prefix = parse.get("prefix")
        building_number = parse.get("building_number")
        cell_api = CellSearchAPI()

        try:
            street_id = await cell_api.get_street_id(street_name, street_prefix)
            cell_info = await cell_api.get_cell_keys(street_id, building_number)
        finally:
            await cell_api.close_session()

        cell = (
            f"{cell_info.get('title')}({cell_info.get('box')})"
            if cell_info
            else "➖"
        )
    else:
        cell = "➖"

    msg = ct.send_task_msg.format(
        task_id,
        task_type_name,
        customer_full_name,
        login,
        address_text,
        cell,
        text,
        task_id,
    )

    try:
        await call.bot.send_message(user_id, msg, reply_markup=keyboard)
        success_message = ct.sent_success.format(task_id, full_name)
        await call.message.edit_text(success_message)
    except aiogram.utils.exceptions.BotBlocked:
        blocked_message = ct.sent_unsuccessful.format(task_id, full_name)
        await call.message.answer(blocked_message)
