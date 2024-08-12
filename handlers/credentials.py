from __future__ import annotations
from collections.abc import Callable
from datetime import datetime

from aiogram import types

import const_texts as ct
from loader import env
from utils.billing import BillingUserData
from utils.keyboards import make_inline_keyboard
from utils.log import logger
from utils.mac_vendor import add_company_name_to_mac_data
from utils.misc import billing, require_group_membership


@require_group_membership(env.list("ALLOWED_CHAT_IDS"))
async def process_users_query(message: types.Message):
    """Processing a request for a list of users.

    Args:
        message (types.Message): The message that contains the request.
    """

    user_query = message.get_args().strip()

    # Check whether the command was sent with the user's login or name
    if not user_query:
        await message.answer(ct.correct_abon_command)
        return

    await message.answer_chat_action(action=types.ChatActions.TYPING)
    async with await billing() as bill:
        users = await bill.find_by_login_or_fio(user_query)

    if not users:
        logger.info("Request %s - no results found.", user_query)
        await message.answer(ct.user_not_found.format(user_query))
        return

    buttons, users_data = [], []

    for num, user in enumerate(users):
        status_session = ""
        access = ""

        balance = float(user["balance_with"])

        if not user["date"]:
            if balance >= 0:
                status_session = " 🟢"
            elif balance < 0:
                status_session = " 🟡"

        if balance < 0:
            access = " 🚫"

        user_status_session = f"{user['login']}{status_session}{access}"
        buttons.append((user_status_session, f"profile__{user['login']}"))
        user_info = (
            num + 1,
            user["login"],
            user["address"],
            user["full_name"],
            user["url_profile"],
        )
        users_data.append(user_info)

    users_data_text = "\n\n".join(
        ct.results_response_users.format(
            num, address, full_name, title=login, url=url
        )
        for num, login, address, full_name, url in users_data
    )
    msg = ct.response_users_text.format(user_query, users_data_text)
    buttons.append((ct.btn_close, "close"))
    keyboard = await make_inline_keyboard(*sum(buttons, ()))

    logger.info("Request %s - processed successfully.", user_query)
    await message.answer(text=msg, reply_markup=keyboard)


async def display_user_profile_menu(call: types.CallbackQuery):
    """Handle the callback query to display the user profile menu."""

    user_login = call.data.split("__")[1]
    msg = ct.selected_user_text.format(user_login)

    buttons = [
        (ct.btn_sessions, f"session__{user_login}"),
        (ct.btn_balance, f"balance__{user_login}"),
        (ct.btn_blank, f"blank__{user_login}"),
        (ct.btn_unblock_inet, f"unblock__{user_login}"),
        (ct.btn_access, f"access__{user_login}"),
        (ct.btn_diagnosis, f"telnet__{user_login}"),
        (ct.btn_close, "close"),
    ]

    keyboard = await make_inline_keyboard(
        *sum(buttons, ()), row_widths=[2, 1, 1, 2, 1]
    )
    logger.info("%s profile has been accessed", user_login)

    await call.message.answer(msg, reply_markup=keyboard)
    await call.answer()


async def send_blank(call: types.CallbackQuery):
    """Sends user account information."""

    await _send_user_info(call, _get_blank_msg)


async def send_session(call: types.CallbackQuery):
    """Send user session information."""

    await _send_user_info(call, _get_session_msg)


async def send_balance(call: types.CallbackQuery):
    """Send user balance information."""

    await _send_user_info(call, _get_balance_msg)


@require_group_membership()
async def send_unblock_inet(call: types.CallbackQuery):
    """Unblock an Internet connection"""

    await _send_user_info(call, _send_unblock_inet_msg)


async def close(call: types.CallbackQuery):
    """Send user close information."""

    await call.message.delete()


async def _send_user_info(
    call: types.CallbackQuery, get_msg_func: Callable[BillingUserData, str]
):
    """
    Send user information using a callback query.

    Args:
        call (types.CallbackQuery): The callback query triggering the function.
        get_msg_func (Callable[[billing, str], str]): A callable function to retrieve user message.
    """

    user_login = call.data.split("__")[1]

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)
    async with await billing() as bill:
        user_profile = await bill.find_by_login(user_login)
        url_profile = user_profile[0].get("url_profile")
        info = await get_msg_func(bill, url_profile)

    keyboard = await make_inline_keyboard(ct.btn_close, "close")
    await call.message.answer(info, reply_markup=keyboard)
    await call.answer()


async def _get_blank_msg(bill: BillingUserData, link: str) -> str:
    """Get the user's account message."""

    blank = await bill.get_credentials_user(link)
    data = "\n".join(
        f"{key}: <code>{value}</code>" for key, value in blank.items()
    )
    msg = ct.credentials_detail.format(data)
    return msg


async def _get_balance_msg(bill: BillingUserData, link: str) -> str:
    balance = await bill.get_balance_user(link)
    msg = "\n".join(f"{key}: {value}" for key, value in balance.items())
    return msg


async def _get_session_msg(bill: BillingUserData, link: str) -> str:
    """Get the user's sessions message."""

    sessions = await bill.get_session_user(link)

    def parse_session_time(session_data):
        """Parse session start and end times, and calculate session duration."""

        current_date = datetime.now().strftime("%d.%m.%y")
        start_time_str = session_data["start"]
        end_time_str = session_data["end"]

        def parse_time(time_str):
            """Parse the given time string into a datetime object."""

            if len(time_str) > 5:
                return datetime.strptime(time_str, "%d.%m.%y %H:%M")
            return datetime.strptime(
                f"{current_date} {time_str}", "%d.%m.%y %H:%M"
            )

        start_time = parse_time(start_time_str)

        try:
            end_time = parse_time(end_time_str)
            session_data["duration"] = end_time - start_time
        except ValueError:
            session_data["end"] += " 🟢"
            session_data["duration"] = (
                datetime.now().replace(microsecond=0) - start_time
            )

    for session in sessions:
        parse_session_time(session)

    # Add mac_address company to session_data
    await add_company_name_to_mac_data(sessions)

    formatted_sessions = [
        ct.sessions_text.format(
            x["start"],
            x["end"],
            x["duration"],
            x["ip"],
            x["mac_company_name"],
            mac=x["mac"],
            url=x["mac"],
        )
        for x in sessions
    ]
    msg = "\n\n".join(formatted_sessions)

    return msg if msg else ct.not_found_session


async def _send_unblock_inet_msg(bill: BillingUserData, link: str) -> str:
    """Response from the server to send unblock message"""
    return await bill.unblock_profile_internet(link)
