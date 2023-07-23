from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def make_inline_keyboard(
        *btn_texts_and_callback_data: str, row_width: int = 1,
) -> InlineKeyboardMarkup:
    """
    Creates an InlineKeyboardMarkup object with the given buttons.
    :param btn_texts_and_callback_data: `Text`, `callback_data_n`
    :param row_width: Row width
    :return: InlineKeyboardMarkup
    """

    group_buttons = InlineKeyboardMarkup(row_width=row_width)

    for i in range(0, len(btn_texts_and_callback_data), 2):
        text = btn_texts_and_callback_data[i]
        callback_data = btn_texts_and_callback_data[i + 1]
        group_buttons.insert(
            InlineKeyboardButton(text=text, callback_data=callback_data))

    return group_buttons


async def make_reply_keyboard(
        words: list[str], row_width: int = 1) -> ReplyKeyboardMarkup:
    """
    Create an ReplyKeyboardMarkup object with the given words
    :param words: Name of the buttons
    :param row_width: Row width
    :return: ReplyKeyboardMarkup
    """

    buttons_group = ReplyKeyboardMarkup(
        row_width=row_width,
        resize_keyboard=True,
    )
    for word in words:
        if word is not None:
            buttons_group.insert(KeyboardButton(text=word))

    return buttons_group
