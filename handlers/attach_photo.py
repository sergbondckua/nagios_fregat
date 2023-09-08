import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiohttp import TCPConnector, ClientTimeout

import const_texts as ct
from loader import env, bot
from state.attach import AttachFile
from utils.keyboards import make_inline_keyboard
from utils.misc import request_processing


async def start_attach_task_photo(call: types.CallbackQuery, state: FSMContext):
    """Start attaching a photo to a task on the user's side."""

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)

    obj_typer, code = call.data.split("__")[1].split("_")
    msg_text = ct.send_photo_to_task.format(code)
    msg = await call.message.answer(msg_text)

    # Set state
    async with state.proxy() as data:
        data["msg_id"] = msg.message_id
        data["obj_typer"] = obj_typer
        data["code"] = code

    await AttachFile.add_file.set()


async def cancel_send(call: types.CallbackQuery, state: FSMContext):
    """Cancel sending a photo."""

    async with state.proxy() as data:
        msg_id = data["msg_id"]

    await call.bot.delete_message(call.message.chat.id, msg_id)
    await call.message.delete()
    await call.answer(ct.cancel_send_done, show_alert=True)
    await state.reset_state()


async def upload_task_photo(message: types.Message, state: FSMContext):
    """Upload a photo of the task to the user's side."""

    await message.answer_chat_action(action=types.ChatActions.TYPING)
    async with state.proxy() as data:
        msg_id = data["msg_id"]
        code = data["code"]
        obj_typer = data["obj_typer"]

    if not message.photo:
        alert_id = data.get("alert_id")
        if alert_id:
            await message.bot.delete_message(message.chat.id, alert_id)

        alert = await message.answer(
            ct.add_photo_or_cancel,
            reply_markup=await make_inline_keyboard(
                ct.btn_cancel_send, "cancel_send"
            ),
        )

        async with state.proxy() as data:
            data["alert_id"] = alert.message_id
        return

    file_id = message.photo[-1].file_id
    url = f"{env.str('URL_USERSIDE')}/oper/class_req.php"
    file_info = await bot.get_file(file_id)
    file_url = await file_info.get_url()
    file_name = file_info.file_path.split("/")[-1]

    async with aiohttp.ClientSession(
        timeout=ClientTimeout(total=5),
        connector=TCPConnector(ssl=False, limit_per_host=10),
    ) as session:
        async with session.get(file_url) as resp:
            if resp.status == 200:
                file_data = await resp.read()  # Get the bytes of the file

    payload = {
        "req_class": "attach",
        "type": "ajax_save_file",
        "obj_typer": obj_typer,
        "obj_code": code,
        "obj_code_second": "",
        "class_id": "574699102",
    }
    file = {"ps_file[]": (file_name, file_data)}

    if await request_processing(url, payload, file):
        msg_text = ct.add_task_photo_msg.format(code, file_name)
    else:
        msg_text = ct.not_found_task_id

    if alert_id := data.get("alert_id"):
        await message.bot.delete_message(message.chat.id, alert_id)

    await message.bot.delete_message(message.chat.id, msg_id)
    await message.delete()

    await message.answer_photo(
        file_id,
        msg_text,
        reply_markup=await make_inline_keyboard(ct.btn_close, "close"),
    )

    await state.finish()
