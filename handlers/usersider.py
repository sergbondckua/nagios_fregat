from __future__ import annotations
from collections.abc import Callable

from aiogram import types

import const_texts as ct
from utils.keyboards import make_inline_keyboard
from utils.misc import userside
from utils.telnet_switch import TelnetSwitch
from utils.userside import UsersideWebDataFetcher


async def send_access_device(call: types.CallbackQuery):
    """Sends device location and access"""

    await _send_info(call, _get_access_device_msg)


async def show_mac_port(call: types.CallbackQuery):
    await _send_info(call, _show_mac_port_msg)


async def show_errors_port(call: types.CallbackQuery):
    await _send_info(call, _show_errors_msg)


async def cable_test(call: types.CallbackQuery):
    await _send_info(call, _cable_test_msg)


async def telnet_menu(call: types.CallbackQuery):
    """Display a menu for Telnet port options based on user's login."""

    user_login = call.data.split("_")[-1]

    buttons = [
        (ct.btn_show_mac, f"show_mac__{user_login}"),
        (ct.btn_show_errors, f"show_errors__{user_login}"),
        (ct.btn_cable_test, f"cable_test__{user_login}"),
        (ct.btn_close, "close"),
    ]
    msg = ct.telnet_menu_diagnostics.format(user_login)
    keyboard = await make_inline_keyboard(*sum(buttons, ()), row_width=1)
    await call.message.answer(msg, reply_markup=keyboard)


async def _send_info(
    call: types.CallbackQuery,
    get_msg_func: Callable[UsersideWebDataFetcher, str],
):
    """Send information based on the provided function."""

    user_login = call.data.split("_")[-1]

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)
    with userside() as data_fetcher:
        if data_fetcher.authenticate():
            info = await get_msg_func(data_fetcher, user_login)

            keyboard = await make_inline_keyboard(ct.btn_close, "close")
            await call.message.answer(info, reply_markup=keyboard)
        else:
            await call.message.answer(ct.not_authorized_userside)


async def _get_access_device_msg(data: UsersideWebDataFetcher, user_login: str):
    """Gets information about the device to which the user is connected"""

    switch_data = data.get_switch_info(user_login)
    user_port = switch_data["user_port"]
    device = switch_data["device"]
    address = switch_data["address"]
    access_device = (
        "No data available"
        if not switch_data["access"]
        else switch_data["access"]
    )
    msg = ct.access_decsriptions.format(
        address, device, user_port, user_login, access_device
    )

    return msg


async def _get_telnet_data(
    data: UsersideWebDataFetcher, user_login: str, action: str
):
    """
    Fetches data using TelnetSwitch based on the given action and user login.

    Args:
        data (UsersideWebDataFetcher): Instance of UsersideWebDataFetcher.
        user_login (str): User's login information.
        action (str): Action to perform, options: "show_mac", "cable_test", "show_errors".

    Returns:
        str: Message containing relevant switch information and result of the action.
    """

    switch_data = data.get_switch_info(user_login)
    address = switch_data["address"]
    device = switch_data["device"]
    user_port = switch_data["user_port"]
    telnet_url = switch_data["telnet_link"]

    async with TelnetSwitch(url=telnet_url, port=user_port) as send_telnet:
        if action == "show_mac":
            result = await send_telnet.show_mac()
        elif action == "cable_test":
            result = await send_telnet.cable_test()
        elif action == "show_errors":
            result = await send_telnet.show_errors()

    msg = ct.telnet_menu_msg.format(
        action,
        user_login,
        user_port,
        address,
        result,
        title=device,
        url=telnet_url,
    )

    return msg


async def _show_mac_port_msg(data: UsersideWebDataFetcher, user_login: str):
    """Fetches and returns a message containing MAC information."""
    return await _get_telnet_data(data, user_login, "show_mac")


async def _show_errors_msg(data: UsersideWebDataFetcher, user_login: str):
    """Fetches and returns a message containing error information."""
    return await _get_telnet_data(data, user_login, "show_errors")


async def _cable_test_msg(data: UsersideWebDataFetcher, user_login: str):
    """Fetches and returns a message containing cable test information."""
    return await _get_telnet_data(data, user_login, "cable_test")
