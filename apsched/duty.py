from aiogram import types

from loader import dp, env
from utils.day_off_duty import DutyScheduler
import const_texts as ct
from utils.db.data_process import DataBaseOperations


async def get_duty_user_info():
    """Retrieve duty user information from the database."""

    db = DataBaseOperations()
    duty_info = await db.get_users_from_db(**{"is_duty": True})
    return dict(duty_info.fetchone()) if duty_info else None


async def send_duty_user_message(duty_user, weekend):
    """Send a duty user message with information about the duty weekend."""

    user_message = ct.msg_duty_user.format(duty_user["full_name"], weekend)
    await dp.bot.send_message(chat_id=duty_user["user_id"], text=user_message)


async def notify_duty(message: types.Message = None):
    """Notify duty assignment on weekends."""

    day_off = await DutyScheduler().get_duty_day_info()
    duty_user = await get_duty_user_info()

    if not duty_user:
        msg = ct.not_found_duty_users
    else:
        weekend = "\n".join(day_off)
        msg = ct.msg_duty_chat.format(
            weekend, duty_user["full_name"], duty_user["username"]
        )

        if not message:
            await send_duty_user_message(duty_user, weekend)

    if message:
        await message.answer(msg)
    else:
        await dp.bot.send_message(chat_id=env.int("CHAT_SUPPORT_ID"), text=msg)


async def assign_next_duty():
    """Assign next duty"""

    duty_info = DutyScheduler()
    msg = ct.not_found_duty_users

    if not await duty_info.assign_duty():
        await dp.bot.send_message(chat_id=env.int("CHAT_SUPPORT_ID"), text=msg)
