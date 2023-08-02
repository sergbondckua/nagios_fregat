import asyncio
from datetime import datetime

from aiogram import types

import const_texts as ct
from utils.keyboards import make_inline_keyboard
from utils.log import logger
from utils.misc import billing, require_group_membership


@require_group_membership()
async def send_user_credentials(message: types.Message):
    """Send user_login credentials with inline keyboard options."""

    await message.answer_chat_action(action=types.ChatActions.TYPING)
    user_login = message.get_args().strip()
    bill = await billing()
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
    finally:
        await bill.close_session()

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

    msg = ct.selected_user_text.format(title=user_login, url=link)
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
    
    user = call.data.split("__")[1]
    bill = await billing()
    link = await bill.get_profile_link(user)
    info = await get_msg_func(bill, link)
    keyboard = await make_inline_keyboard(ct.btn_close, "close")
    
    await bill.close_session()
    await call.message.answer(info, reply_markup=keyboard)


async def _get_blank_msg(bill: billing, link: str) -> str:
    """Get the user's account message."""

    blank = await bill.get_credentials_user(link)
    data = "\n".join(
        f"{key}: <code>{value}</code>" for key, value in blank.items()
    )
    msg = ct.credentials_detail.format(data)
    return msg


async def _get_session_msg(bill: billing, link: str) -> str:
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


async def _get_balance_msg(bill: billing, link: str) -> str:
    balance = await bill.get_balance_user(link)
    msg = "\n".join(f"{key}: {value}" for key, value in balance.items())
    return msg
