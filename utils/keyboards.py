from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def make_inline_keyboard(
    *btn_texts_and_callback_data: str,
    row_widths: list = None,
) -> InlineKeyboardMarkup:
    """
    Creates an InlineKeyboardMarkup object with the given buttons.
    :param btn_texts_and_callback_data: `Text`, `callback_data_n`
    :param row_widths: List of row widths (optional)
    :return: InlineKeyboardMarkup
    """

    buttons_group = InlineKeyboardMarkup()

    index = 0

    # If row_widths is not provided, set a default row width of 1
    if not row_widths:
        row_widths = [1] * len(btn_texts_and_callback_data)

    for row_width in row_widths:
        row_buttons = []
        for _ in range(row_width):
            if index >= len(btn_texts_and_callback_data):
                break

            text = btn_texts_and_callback_data[index]
            callback_data = btn_texts_and_callback_data[index + 1]
            row_buttons.append(
                InlineKeyboardButton(text=text, callback_data=callback_data)
            )

            index += 2

        buttons_group.row(*row_buttons)

    return buttons_group


async def make_reply_keyboard(
    words: list[str], row_widths: list = None
) -> ReplyKeyboardMarkup:
    """
    Create a ReplyKeyboardMarkup object with the given words
    :param words: List of words for buttons
    :param row_widths: List of row widths (optional)
    :return: ReplyKeyboardMarkup
    """

    buttons_group = ReplyKeyboardMarkup(
        resize_keyboard=True,
    )

    index = 0

    # If row_widths is not provided, set a default row width of 1
    if not row_widths:
        row_widths = [1] * len(words)

    for row_width in row_widths:
        row_buttons = []
        for _ in range(row_width):
            if index >= len(words):
                break

            word = words[index]
            if word is not None:
                row_buttons.append(KeyboardButton(text=word))

            index += 1

        buttons_group.row(*row_buttons)

    return buttons_group
