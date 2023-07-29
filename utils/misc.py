from __future__ import annotations
from datetime import datetime, time

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import MessageIsTooLong
from pytz import timezone

from loader import env
from utils.log import logger
from utils.nagios import GetCriticalHostNagios


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
        parts = [text[i:i + 4096] for i in range(0, len(text), 4096)]

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
