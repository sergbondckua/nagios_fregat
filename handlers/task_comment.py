from aiogram import types
from aiogram.dispatcher import FSMContext
import aiogram.utils.emoji as emoji_utils

from loader import env
import const_texts as ct
from state.comment import AddComment
from utils.keyboards import make_inline_keyboard
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
        "opis": emoji_utils.demojize(comment),
    }

    if await request_processing(url, payload):
        msg = ct.add_task_comment_msg.format(code, comment)
    else:
        msg = ct.not_found_task_id

    await message.answer(msg)


async def start_add_task_comment(call: types.CallbackQuery, state: FSMContext):
    """Start adding a task comment"""

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)
    await AddComment.add_comment.set()  # Set state
    task_id = call.data.split("__")[1]
    msg = await call.message.answer(ct.write_comment)

    async with state.proxy() as data:
        data["task_id"] = task_id
        data["msg_id"] = msg.message_id


async def pre_send_comment(message: types.Message, state: FSMContext):
    """Prepare to send a comment"""

    await message.answer_chat_action(action=types.ChatActions.TYPING)

    full_name = message.from_user.full_name
    typical_comment = ct.typical_comment.format(full_name)
    text = message.text
    comment = (
        typical_comment
        if text.lower() in {"+", "ok", "ок", "done"}
        else ct.comment_msg.format(full_name, text)
    )

    msg = emoji_utils.demojize(comment)
    await message.delete()
    await message.answer(
        ct.pre_send_comment.format(msg),
        reply_markup=await make_inline_keyboard(
            ct.btn_approve_send,
            "approve_send",
            ct.btn_cancel_comment,
            "cancel_comment",
            row_width=2,
        ),
    )

    async with state.proxy() as data:
        data["comment"] = msg
        msg_id = data["msg_id"]

    await message.bot.delete_message(message.chat.id, msg_id)
    await AddComment.next()


async def send_comment(call: types.CallbackQuery, state: FSMContext):
    """Send the prepared comment"""

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)

    async with state.proxy() as data:
        task_id = data.get("task_id")
        comment = data.get("comment")

    url = f"{env.str('URL_USERSIDE')}oper/journal.php"
    payload = {
        "type": "working",
        "type2": "new_comment2",
        "ret": None,
        "code": task_id,
        "standart_comment": 6,
        "opis": comment,
    }

    if await request_processing(url, payload):
        msg = ct.add_task_comment_msg.format(task_id, comment)
    else:
        msg = ct.not_found_task_id

    await call.message.delete()
    await call.message.answer(msg)
    await state.finish()


async def cancel_comment(call: types.CallbackQuery, state: FSMContext):
    """Cancel the comment and reset the state"""

    await call.message.delete()
    await call.answer(ct.cancel_comment, show_alert=True)
    await state.reset_state()
