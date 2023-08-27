from aiogram import types

from loader import env
import const_texts as ct
from utils.misc import userside


async def request_processing(url, payload: dict) -> bool:
    """Send a request to the server and return True if successful"""

    with userside() as data_fetcher:
        if not data_fetcher.authenticate():
            return False

        return data_fetcher.send_server_request(url, payload)


async def add_task_comment(message: types.Message) -> None:
    """Add a task comment to the Userside"""

    await message.answer_chat_action(action=types.ChatActions.TYPING)

    full_name = message.from_user.full_name
    args = message.get_args().split(":")
    url = f"{env.str('URL_USERSIDE')}oper/journal.php"

    if len(args) < 2:
        await message.answer(ct.correct_abon_command)
        return

    code = args[0]
    comment = f"{full_name}:\n" + " ".join(args[1:])

    payload = {
        "type": "working",
        "type2": "new_comment2",
        "ret": None,
        "code": code,
        "standart_comment": 6,
        "opis": comment,
    }

    if await request_processing(url, payload):
        await message.answer(ct.add_task_comment_msg.format(code, comment))
    else:
        await message.answer(ct.not_found_task_id)
