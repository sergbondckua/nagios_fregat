from aiogram import types
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.markdown import text, hbold, quote_html, hcode


async def cmd_info_id(message: types.Message):
    """Return user ID information"""

    full_name = message.from_user.full_name
    userid = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.mention if message.from_user.mention else "➖"

    if types.ChatType.PRIVATE != message.chat.type:
        title = message.chat.title
    else:
        title = full_name

    msg = text(
        hbold("Your ID information:"),
        text("🚻", hbold("Full name:"), quote_html(full_name)),
        text("🪪", hbold("Username:"), quote_html(username)),
        text("🆔", hbold("Your ID:"), hcode(userid)),
        text("💬", hbold("Chat ID:"), hcode(chat_id)),
        text("🔸", hbold("Title:"), hcode(title)),
        sep="\n",
    )
    await types.ChatActions.typing()
    await message.answer(text=msg)


async def get_ref(message: types.Message):
    """Handler for creating an mounter referral link"""

    link = await get_start_link("mounter", encode=False)
    await message.answer(f"Посилання монтажника: {link}")
