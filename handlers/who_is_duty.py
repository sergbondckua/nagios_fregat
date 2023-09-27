from aiogram import types

from utils.db.data_process import DataBaseOperations


async def who_is_duty(message: types.Message):
    """Sends a message who is duty"""
    db = DataBaseOperations()
    duty_info = await db.get_users_from_db(**{"is_duty": True})
    duty_user = dict(duty_info.fetchone())
    msg = duty_user["full_name"] if duty_user else "There is no next one"

    await message.answer(msg)
