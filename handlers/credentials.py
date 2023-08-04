from __future__ import annotations
from collections.abc import Callable
from datetime import datetime

from aiogram import types

import const_texts as ct
from utils.billing import BillingUserData
from utils.keyboards import make_inline_keyboard
from utils.log import logger
from utils.misc import billing, require_group_membership


@require_group_membership()
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

    users_data_for_button = [
        (
            f"{user['address']} 🟢"
            if not user["date"]
            else f"{user['address']}",
            f"profile__{user['login']}",
        )
        for user in users
    ]

    keyboard = await make_inline_keyboard(*sum(users_data_for_button, ()))

    logger.info("Request %s - processed successfully.", user_query)

    await message.answer(
        text=ct.get_users_list_text.format(user_query), reply_markup=keyboard
    )


async def display_user_profile_menu(call: types.CallbackQuery):
    """Handle the callback query to display the user profile menu."""

    user_login = call.data.split("__")[1]
    msg = ct.selected_user_text.format(user_login)

    buttons = [
        (ct.btn_sessions, f"session__{user_login}"),
        (ct.btn_balance, f"balance__{user_login}"),
        (ct.btn_blank, f"blank__{user_login}"),
        (ct.btn_close, "close"),
    ]

    keyboard = await make_inline_keyboard(*sum(buttons, ()), row_width=3)

    logger.info("%s profile has been accessed", user_login)
    await call.message.edit_text(msg, reply_markup=keyboard)


async def send_blank(call: types.CallbackQuery):
    """Sends user account information."""

    await _send_user_info(call, _get_blank_msg)


async def send_session(call: types.CallbackQuery):
    """Send user session information."""

    await _send_user_info(call, _get_session_msg)


async def send_balance(call: types.CallbackQuery):
    """Send user balance information."""

    await _send_user_info(call, _get_balance_msg)


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


async def _get_blank_msg(bill: BillingUserData, link: str) -> str:
    """Get the user's account message."""

    blank = await bill.get_credentials_user(link)
    data = "\n".join(
        f"{key}: <code>{value}</code>" for key, value in blank.items()
    )
    msg = ct.credentials_detail.format(data)
    return msg


async def _get_session_msg(bill: BillingUserData, link: str) -> str:
    """Get the user's sessions message."""

    sessions = await bill.get_session_user(link)

    # Add the time that the session lasted
    for session in sessions:
        if len(session["start"]) > 5:
            # If there is a date, then we parse the date and time
            start = datetime.strptime(session["start"], "%d.%m.%y %H:%M")
        else:
            # If there is no date, then we add the current date
            current_date = datetime.now().strftime("%d.%m.%y")
            start = datetime.strptime(
                f"{current_date} {session['start']}", "%d.%m.%y %H:%M"
            )

        try:
            if len(session["end"]) > 5:
                end = datetime.strptime(session["end"], "%d.%m.%y %H:%M")
                session["duration"] = end - start
            else:
                session["duration"] = (
                    datetime.now().replace(microsecond=0) - start
                )
        except ValueError:
            session["end"] = session["end"] + " 🟢"
            session["duration"] = datetime.now().replace(microsecond=0) - start

    msg = "\n\n".join(
        ct.sessions_text.format(
            x["start"], x["end"], x["duration"], x["ip"], x["mac"]
        )
        for x in sessions
    )
    return msg if msg else ct.not_found_session


async def _get_balance_msg(bill: BillingUserData, link: str) -> str:
    balance = await bill.get_balance_user(link)
    msg = "\n".join(f"{key}: {value}" for key, value in balance.items())
    return msg
