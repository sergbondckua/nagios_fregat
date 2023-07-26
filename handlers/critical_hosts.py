from aiogram import types

import const_texts as ct
from loader import is_night_time, get_all_critical_hosts_info
from utils.keyboards import make_inline_keyboard
from utils.log import logger


async def send_critical_hosts_message(message: types.Message):
    """Sends a notification with all critical hosts"""

    if hosts := await get_all_critical_hosts_info():
        # Convert the list of changed hosts to a formatted string
        hosts_str = "\n".join(ct.host_name_row % (i[0],) for i in hosts)

        keyboard = await make_inline_keyboard(ct.btn_detail, "details")

        await message.answer(
            text=ct.all_down_hosts % (len(hosts), hosts_str),
            disable_notification=is_night_time(),
            reply_markup=keyboard,
        )
        logger.info(
            "Critical hosts: %s. Sent to Telegram chat: %s", len(hosts), message.chat.id
        )
    else:
        await message.answer(
            text=ct.all_ok,
            disable_notification=is_night_time(),
        )
        logger.warning("No critical hosts found. Data is empty.")


async def send_detailed_critical_hosts_message(call: types.CallbackQuery):
    """Sends all the details of all hosts that are down."""

    await call.message.edit_reply_markup()
    await call.message.delete()

    if hosts := await get_all_critical_hosts_info():
        # Convert the list of changed hosts to a formatted string
        hosts_str = "\n\n".join(
            ct.host_detail_name_row % (i[0], i[1], i[2]) for i in hosts)

        await call.message.answer(
            text=ct.all_down_hosts % (len(hosts), hosts_str),
        )
        logger.info(
            "Critical detailed hosts: %s. Sent to Telegram chat: %s",
            len(hosts),
            call.message.chat.id,
        )
