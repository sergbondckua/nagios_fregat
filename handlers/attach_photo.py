import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext

import const_texts as ct
from loader import env, bot
from state.attach import AttachFile
from utils.keyboards import make_inline_keyboard
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
    keyboard = await make_inline_keyboard("Скасувати", "cancel_send")
    await call.message.answer(
        "Прикрепите фотографию к заданию", reply_markup=keyboard
    )


async def cancel_send(call: types.CallbackQuery, state: FSMContext):
    """TODO: implement"""

    await state.reset_state()
    await call.message.delete()
    await call.answer("Відправка фото скасовано.", show_alert=True)


async def upload_task_photo(message: types.Message, state: FSMContext) -> None:
    """Upload a photo of the task to the user's side."""

    await message.answer_chat_action(action=types.ChatActions.TYPING)

    async with state.proxy() as data:
        code = data["code"]
        obj_typer = data["obj_typer"]
    await state.finish()

    file_id = message.photo[-1].file_id
    url = f"{env.str('URL_USERSIDE')}/oper/class_req.php"
    file_info = await bot.get_file(file_id)
    file_url = await file_info.get_url()
    file_name = file_info.file_path.split("/")[-1]

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            if resp.status == 200:
                # We get the bytes of the file
                file_data = await resp.read()

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
        msg = ct.add_task_comment_msg.format(code, file_url)
    else:
        msg = ct.not_found_task_id

    await message.answer(msg)
