from __future__ import annotations

from datetime import datetime, time
from functools import wraps

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import MessageIsTooLong
from pytz import timezone

import const_texts as ct
from loader import env, dp, bot
from utils.billing import BillingUserData
from utils.log import logger
from utils.nagios import GetCriticalHostNagios
from utils.userside import UsersideWebDataFetcher


async def is_user_member(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.is_chat_member()
    except Exception:  # noqa pylint: disable=broad-except
        return False


def require_group_membership(group_id: int = env.int("CHAT_SUPPORT_ID")):
    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id

            if await is_user_member(group_id, user_id):
                return await func(message, *args, **kwargs)
            logger.info(
                "Access is denied. User %s is not a member of group %s",
                user_id,
                group_id,
            )
            await message.answer(
                ct.require_group_member_text.format(message.from_user.full_name)
            )

        return wrapped

    return decorator


def is_night_time():
    """
    Checks if the current time is within the night hours.

    Returns:
        bool: True if the current time is during the night, False otherwise.
    """

    now = datetime.now(tz=timezone(env.str("TZ"))).time()
    start_night_time = time(22, 0)
    end_night_time = time(7, 0)

    return start_night_time <= now or now <= end_night_time


async def get_all_critical_hosts_info():
    """Get information about all critical hosts."""

    parser = GetCriticalHostNagios(
        url=env.str("URL_NAGIOS"),
        login=env.str("LOGIN_NAGIOS"),
        passwd=env.str("PASSWD_NAGIOS"),
    )

    return await parser.get_all_critical_hosts()


async def billing() -> BillingUserData:
    bill = BillingUserData(
        url=env.str("URL_BILLING"),
        login=env.str("LOGIN_BILLING"),
        passwd=env.str("PASSWD_BILLING"),
    )
    return bill


def userside():
    auth = UsersideWebDataFetcher(
        base_url=env.str("URL_USERSIDE"),
        login=env.str("LOGIN_USERSIDE"),
        password=env.str("PASSWD_USERSIDE"),
    )
    return auth


async def send_message_with_retry(
    message: types.Message | Dispatcher,
    text: str,
    chat_id: int | None = None,
    keyboard: types.InlineKeyboardMarkup | None = None,
):
    """
    Send the message, and if it's too long,
    split and send as separate messages.

    :param message: The message object that triggered the function.
    :param text: The text of the message to be sent.
    :param keyboard: (Optional) The inline keyboard to be sent with the message.
    :param chat_id: (Optional) The ID of the chat to send the message to.
    """

    try:
        if chat_id:
            await message.bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_notification=is_night_time(),
                reply_markup=keyboard,
            )
        else:
            await message.answer(
                text=text,
                disable_notification=is_night_time(),
                reply_markup=keyboard,
            )
    except MessageIsTooLong:
        # Extra long message > 4096 characters
        parts = [text[i : i + 4096] for i in range(0, len(text), 4096)]

        # Sending each part as a separate message
        for part in parts:
            if chat_id:
                await message.bot.send_message(
                    chat_id=chat_id,
                    text=part,
                    disable_notification=is_night_time(),
                )
            else:
                await message.answer(
                    text=part,
                    disable_notification=is_night_time(),
                )

        logger.info(
            "Extra long message (%s) was split into %s messages.",
            len(text),
            len(parts),
        )
