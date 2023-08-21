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
    await _send_info(call, _get_mac_port_device_msg)


async def show_errors_port(call: types.CallbackQuery):
    await _send_info(call, _make_show_errors_msg)


async def make_cable_test(call: types.CallbackQuery):
    await _send_info(call, _make_cable_test_msg)


async def telnet_menu(call: types.CallbackQuery):
    """TODO:"""

    user_login = call.data.split("_")[-1]

    # TODO: const text
    buttons = [
        ("Show mac", f"show_mac__{user_login}"),
        ("Show errors", f"show_errors__{user_login}"),
        ("Cable test", f"cable_test__{user_login}"),
        (ct.btn_close, "close"),
    ]
    keyboard = await make_inline_keyboard(*sum(buttons, ()), row_width=1)
    await call.message.answer(user_login, reply_markup=keyboard)


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
            await call.message.answer("Not auth Userside")


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
    # TODO: add constants text
    msg = f"Адреса: {address}\nПристрій: {device}\nПорт абонента: {user_port}\nОпис доступу: {access_device}"

    return msg


async def _get_mac_port_device_msg(
    data: UsersideWebDataFetcher, user_login: str
):
    switch_data = data.get_switch_info(user_login)
    address = switch_data["address"]
    device = switch_data["device"]
    user_port = switch_data["user_port"]
    telnet_url = switch_data["telnet_link"]
    async with TelnetSwitch(url=telnet_url, port=user_port) as send_telnet:
        mac = await send_telnet.show_mac()

    msg = ct.text(user_login, user_port, address, device, mac, sep="\n")

    return msg


async def _make_cable_test_msg(data: UsersideWebDataFetcher, user_login: str):
    switch_data = data.get_switch_info(user_login)
    address = switch_data["address"]
    device = switch_data["device"]
    user_port = switch_data["user_port"]
    telnet_url = switch_data["telnet_link"]
    async with TelnetSwitch(url=telnet_url, port=user_port) as send_telnet:
        test = await send_telnet.cable_test()

    msg = ct.text(
        user_login, user_port, address, device, ct.hcode(test), sep="\n"
    )

    return msg


async def _make_show_errors_msg(data: UsersideWebDataFetcher, user_login: str):
    switch_data = data.get_switch_info(user_login)
    address = switch_data["address"]
    device = switch_data["device"]
    user_port = switch_data["user_port"]
    telnet_url = switch_data["telnet_link"]
    async with TelnetSwitch(url=telnet_url, port=user_port) as send_telnet:
        test = await send_telnet.show_errors()

    msg = ct.text(
        user_login, user_port, address, device, ct.hcode(test), sep="\n"
    )

    return msg
