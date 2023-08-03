from __future__ import annotations
import asyncio
from datetime import datetime

from aiogram import types

import const_texts as ct
from utils.billing import BillingUserData
from utils.keyboards import make_inline_keyboard
from utils.log import logger
from utils.misc import billing, require_group_membership


async def get_users_list(message: types.Message):
    """List users"""

    # Check whether the command was sent with the user's login
    if not message.get_args():
        await message.answer(ct.correct_abon_command)
        return

    await message.answer_chat_action(action=types.ChatActions.TYPING)
    user_query = message.get_args().strip()
    async with await billing() as bill:
        users = await bill.find_by_login_or_fio(user_query)

    if not users:
        await message.answer(ct.user_not_found.format(user_query))
        return

    users_data_for_button = [
        (
            f"🟢 {user['address']}",
            f"profile__{user['login']}",
        )
        if not user["date"]
        else (
            f"🔴 {user['address']}",
            f"profile__{user['login']}__{user['url_profile']}",
        )
        for user in users
    ]
    keyboard = await make_inline_keyboard(*sum(users_data_for_button, ()))
    # TODO: const text
    await message.answer(
        text=f"Знайдено за вашим запитом: {user_query}", reply_markup=keyboard
    )


async def get_user_profile_credentials(call: types.CallbackQuery):
    """TODO:"""
    user_login = call.data.split("__")[1]
    msg = ct.selected_user_text.format(title=user_login, url="#")
    keyboard = await make_inline_keyboard(
        ct.btn_sessions,
        f"session__{user_login}",
        ct.btn_balance,
        f"balance__{user_login}",
        ct.btn_blank,
        f"blank__{user_login}",
        ct.btn_close,
        "close",
        row_width=3,
    )

    await call.message.answer(msg, reply_markup=keyboard)


@require_group_membership()
async def send_user_credentials(message: types.Message | types.CallbackQuery):
    """Send user_login credentials with inline keyboard options."""

    # Check whether the command was sent with the user's login
    if not message.get_args():
        await message.answer(ct.correct_abon_command)
        return

    await message.answer_chat_action(action=types.ChatActions.TYPING)
    user_login = message.get_args().strip()

    async with await billing() as bill:
        try:
            link = await bill.get_profile_link(user_login)
        except asyncio.TimeoutError:
            logger.error(
                "Timeout error while sending user_login credentials to %s",
                user_login,
            )
            await message.answer(ct.timeout_error)
            return
        except ValueError:
            logger.warning("User %s not found.", user_login)
            await message.answer(ct.user_not_found.format(user_login))
            return

    msg = ct.selected_user_text.format(title=user_login, url=link)
    keyboard = await make_inline_keyboard(
        ct.btn_sessions,
        f"session__{user_login}",
        ct.btn_balance,
        f"balance__{user_login}",
        ct.btn_blank,
        f"blank__{user_login}",
        ct.btn_close,
        "close",
        row_width=3,
    )

    await message.answer(msg, reply_markup=keyboard)
    logger.info("%s profile has been accessed", user_login)


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


async def _send_user_info(call: types.CallbackQuery, get_msg_func):
    """Send user information using a callback query."""

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)

    url_profile = call.data.split("__")[2]
    async with await billing() as bill:
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
