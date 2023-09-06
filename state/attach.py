from aiogram.dispatcher.filters.state import StatesGroup, State


class AttachFile(StatesGroup):
    """State class for attaching"""
    add_file = State()
