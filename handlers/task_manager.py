from __future__ import annotations
from collections.abc import Callable

from aiogram import types

import const_texts as ct
from utils.api_userside.api import ApiUsersideData
from utils.db.data_process import DataBaseOperations
from utils.keyboards import make_inline_keyboard
from utils.telnet_switch import TelnetSwitch


async def task_assignment(message: types.Message):
    task_id = message.get_args().strip()
    if not task_id:
        await message.answer(ct.correct_abon_command)
        return
    await message.answer_chat_action(action=types.ChatActions.TYPING)
    api_data = ApiUsersideData()
    task_data = await api_data.get_task(task_id)
    customer_id = task_data["Data"]["customer"]["id"]
    customer_data = await api_data.get_customer(customer_id)

    msg = (
        f"#{task_data['Data']['id']} - {task_data['Data']['type']['name']}"
        f"Abonent: {customer_data['Data']['full_name']} {customer_data['Data']['phone'][1]['number']}"
        f"<code>/abon chk_{task_data['Data']['customer']['login']}</code>"
        f"Адреса завдання: {task_data['Data']['address']['text']}"
        f"\n\n{await TelnetSwitch.replace_br_nbsp(task_data['Data']['description'])}"
    )
    list_data = await DataBaseOperations().get_users_profile_from_db()
    keyboard = await make_inline_keyboard(*sum([(i["full_name"], f"send_to__{i['user_id']}") for i in list_data], ()))

    await message.answer(msg, reply_markup=keyboard)
