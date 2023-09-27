from loader import dp, env
from utils.day_off_duty import DutyScheduler
import const_texts as ct


async def set_and_notify_duty():
    """Appointment of duty on weekends with notice"""

    duty_scheduler = DutyScheduler()
    duty_info = await duty_scheduler.get_duty_day_info()

    if not duty_info:
        msg = ct.not_found_duty_users
    else:
        weekend = "\n".join(duty_info["weekend"])
        user_duty = duty_info["user_duty"]
        msg = ct.msg_duty_chat.format(
            weekend, user_duty["full_name"], user_duty["username"]
        )

        user_message = ct.msg_duty_user.format(user_duty["full_name"], weekend)

        await dp.bot.send_message(
            chat_id=user_duty["user_id"], text=user_message
        )

    await dp.bot.send_message(chat_id=env.int("CHAT_SUPPORT_ID"), text=msg)
