import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext

import const_texts as ct
from loader import env, bot
from state.attach import AttachFile
from utils.misc import request_processing


async def start_attach_task_photo(call: types.CallbackQuery, state: FSMContext):
    """Start attaching a photo to a task on the user's side."""

    await call.message.answer_chat_action(action=types.ChatActions.TYPING)
    obj_typer, code = call.data.split("__")[1].split("_")

    # Set state
    async with state.proxy() as data:
        data["obj_typer"] = obj_typer
        data["code"] = code

    await AttachFile.add_file.set()
    await call.message.answer("Прикрепите фотографию к заданию")


async def upload_task_photo(message: types.Message, state: FSMContext) -> None:
    """Upload a photo of the task to the user's side."""

    await message.answer_chat_action(action=types.ChatActions.TYPING)
    file_id = message.photo[-1].file_id
    url = f"{env.str('URL_USERSIDE')}/oper/class_req.php"
    async with state.proxy() as data:
        code = data["code"]
        obj_typer = data["obj_typer"]
    await state.finish()

    file_info = await bot.get_file(file_id)
    file_url = file_info.file_path

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                file_data = await response.read()

    payload = {
        "req_class": "attach",
        "type": "ajax_save_file",
        "obj_typer": obj_typer,
        "obj_code": code,
        "obj_code_second": "",
        "class_id": "574699102",
    }
    files = {"ps_file[]": (file_info.file_id + ".png", file_data)}

    if await request_processing(url, payload, files):
        msg = ct.add_task_comment_msg.format(code, file_url)
    else:
        msg = ct.not_found_task_id

    await message.answer(msg)
