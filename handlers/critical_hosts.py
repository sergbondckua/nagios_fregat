from aiogram import types
from aiogram.utils.exceptions import MessageIsTooLong

import const_texts as ct
from utils.keyboards import make_inline_keyboard
from utils.log import logger
from utils.misc import get_all_critical_hosts_info, is_night_time


async def send_message_with_retry(
    message: types.Message, text: str, keyboard=None
):
    """
        Send the message, and if it's too long,
        split and send as separate messages.
    """

    try:
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
            await message.answer(
                text=part,
                disable_notification=is_night_time(),
            )

        logger.info(
            "Extra long message (%s) was split into %s messages.",
            len(text),
            len(parts),
        )


async def send_critical_hosts_message(message: types.Message):
    """Sends a notification with all critical hosts"""
    hosts = await get_all_critical_hosts_info()

    if hosts:
        # Convert the list of changed hosts to a formatted string
        hosts_str = "\n".join(
            ct.host_name_row.format(name) for name, *_ in hosts
        )

        keyboard = await make_inline_keyboard(ct.btn_detail, "details")
        msg = ct.all_down_hosts.format(len(hosts), hosts_str)

        await send_message_with_retry(
            message,
            text=msg,
            keyboard=keyboard,
        )

        logger.info(
            "Critical hosts: %s. Sent to Telegram chat: %s",
            len(hosts),
            message.chat.id,
        )
    else:
        await send_message_with_retry(
            message,
            text=ct.all_ok,
        )
        logger.warning("No critical hosts found. Data is empty.")


async def send_detailed_critical_hosts_message(call: types.CallbackQuery):
    """Sends all the details of all hosts that are down."""
    await call.message.edit_reply_markup()
    await call.message.delete()

    hosts = await get_all_critical_hosts_info()

    if hosts:
        # Convert the list of changed hosts to a formatted string
        hosts_str = "\n\n".join(
            ct.host_detail_name_row.format(name, downtime, ip)
            for name, downtime, ip in hosts
        )

        text = ct.all_down_hosts.format(len(hosts), hosts_str)

        await send_message_with_retry(
            call.message,
            text=text,
        )

        logger.info(
            "Critical detailed hosts: %s. Sent to Telegram chat: %s",
            len(hosts),
            call.message.chat.id,
        )
