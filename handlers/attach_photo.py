from aiogram import types
from aiogram.dispatcher import FSMContext

from state.attach import AttachFile


async def attach_task_photo(call: types.CallbackQuery):
    """Attach a task photo to the Userside."""

    # Set state
    await AttachFile.add_file.set()

    await call.message.answer("Attach task photo")


async def add_task_photo(message: types.Message, state: FSMContext):
    """Add a task photo to the Userside"""

    file_id = message.photo[-1].file_id
    await state.update_data(file_id=file_id)
    await message.answer("Add task photo")
    await state.finish()
