from aiogram.dispatcher.filters.state import StatesGroup, State


class AddComment(StatesGroup):
    """State class for send comment"""
    add_comment = State()
    approve_comment = State()
