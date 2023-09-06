from aiogram import types

from loader import env
import const_texts as ct
from utils.misc import request_processing


async def add_task_comment(message: types.Message) -> None:
    """Add a task comment to the Userside"""

    await message.answer_chat_action(action=types.ChatActions.TYPING)

    full_name = message.from_user.full_name
    args = message.get_args().split(":")
    url = f"{env.str('URL_USERSIDE')}oper/journal.php"

    if len(args) < 2:
        await message.answer(ct.correct_abon_command)
        return

    code, text = args[0], " ".join(args[1:])
    typical_comment = f"{full_name}:\n{ct.typical_comment}"
    comment = f"{full_name}:\n{text}" if text else typical_comment

    payload = {
        "type": "working",
        "type2": "new_comment2",
        "ret": None,
        "code": code,
        "standart_comment": 6,
        "opis": comment,
    }

    if await request_processing(url, payload):
        msg = ct.add_task_comment_msg.format(code, comment)
    else:
        msg = ct.not_found_task_id

    await message.answer(msg)
