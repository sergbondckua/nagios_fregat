import asyncio

from aiogram import types

import const_texts as ct
from utils.keyboards import make_inline_keyboard
from utils.log import logger
from utils.misc import billing


async def send_user_credentials(message: types.Message):
    """Send user_login credentials with inline keyboard options."""

    user_login = message.get_args().strip()
    bill = await billing()
    try:
        await bill.get_profile_link(user_login)
    except asyncio.TimeoutError:
        await message.answer("Помилка очікування!")
        return
    except ValueError:
        await message.answer("Користувача з таким логіном не знайдено.")
        return
    finally:
        await bill.close_session()

    keyboard = await make_inline_keyboard(
        "Сеанси",
        f"seance__{user_login}",
        "Баланс",
        f"balance__{user_login}",
        "Налаштування",
        f"blank__{user_login}",
        "Закрити",
        "close",
        row_width=3,
    )

    msg = user_login
    await message.answer(msg, reply_markup=keyboard)


async def send_blank(call: types.CallbackQuery):
    """Sends user account information."""

    await _send_user_info(call, _get_blank_msg)


async def send_seance(call: types.CallbackQuery):
    """Send user session information."""

    await _send_user_info(call, _get_seance_msg)


async def send_balance(call: types.CallbackQuery):
    """Send user balance information."""

    await _send_user_info(call, _get_balance_msg)


async def close(call: types.CallbackQuery):
    """ "Send user close information."""

    await call.message.delete()


async def _send_user_info(call: types.CallbackQuery, get_msg_func):
    user = call.data.split("__")[1]
    bill = await billing()
    link = await bill.get_profile_link(user)
    info = await get_msg_func(bill, link)
    await bill.close_session()

    await call.bot.send_chat_action(
        call.message.chat.id, action=types.ChatActions.TYPING
    )
    await call.message.answer(info)


async def _get_blank_msg(bill, link):
    blank = await bill.get_credentials_user(link)
    msg = "\n".join(
        f"{key}: <code>{value}</code>" for key, value in blank.items()
    )
    return msg


async def _get_seance_msg(bill, link):
    seance = await bill.get_seance_user(link)
    msg = "\n\n".join(f"<pre>{x}</pre>" for x in seance)
    return msg


async def _get_balance_msg(bill, link):
    balance = await bill.get_balance_user(link)
    msg = "\n".join(f"{key}: {value}" for key, value in balance.items())
    return msg
