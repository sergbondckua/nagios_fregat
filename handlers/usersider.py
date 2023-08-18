from __future__ import annotations
from collections.abc import Callable

from aiogram import types

import const_texts as ct
from utils.keyboards import make_inline_keyboard
from utils.misc import userside
from utils.userside import UsersideWebDataFetcher


async def send_access_device(call: types.CallbackQuery):
    """Sends device location and access"""

    await _send_info(call, _get_access_device_msg)


async def _send_info(
    call: types.CallbackQuery,
    get_msg_func: Callable[UsersideWebDataFetcher, str],
):
    """Send information based on the provided function."""

    user_login = call.data.split("_")[-1]

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)
    with userside() as data_fetcher:
        if data_fetcher.authenticate():
            info = get_msg_func(data_fetcher, user_login)

            keyboard = await make_inline_keyboard(ct.btn_close, "close")
            await call.message.answer(info, reply_markup=keyboard)
        else:
            return await call.message.answer("Not auth Userside")


def _get_access_device_msg(data: UsersideWebDataFetcher, user_login: str):
    """Gets information about the device to which the user is connected"""

    switch_data = data.get_switch_info(user_login)
    access_device = switch_data.get("access")

    return access_device if access_device else "No data available"
