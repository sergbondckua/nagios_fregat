from __future__ import annotations

import locale
import re
from datetime import datetime, time
from functools import wraps

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import MessageIsTooLong
from pytz import timezone

import const_texts as ct
from loader import env, bot
from utils.billing import BillingUserData
from utils.log import logger
from utils.nagios import GetCriticalHostNagios
from utils.userside import UsersideWebDataFetcher


async def is_user_member(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.is_chat_member()
    except Exception:  # noqa pylint: disable=broad-except
        return False


def require_group_membership(allowed_chat_ids: list[int] = None):
    """
    Decorator that checks if a user is a member of the allowed groups before executing the function.
    """

    if allowed_chat_ids is None:
        allowed_chat_ids = []

    # Add support and chief chat IDs from environment variables
    allowed_chat_ids += env.list("CHAT_SUPPORT_ID") + env.list("CHIEF_IDS")

    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id
            for chat_id in allowed_chat_ids:
                if await is_user_member(chat_id, user_id):
                    return await func(message, *args, **kwargs)
            logger.info(
                "Access is denied. "
                "User %s is not in ALLOWED_CHAT_IDS or CHAT_SUPPORT_ID %s",
                user_id,
                allowed_chat_ids,
            )
            await message.answer(
                ct.require_group_member_text.format(message.from_user.full_name)
            )

        return wrapped

    return decorator


def is_night_time() -> bool:
    """
    Checks if the current time is within the night hours.

    Returns:
        bool: True if the current time is during the night, False otherwise.
    """

    now = datetime.now(tz=timezone(env.str("TZ"))).time()
    start_night_time = time(22, 0)
    end_night_time = time(7, 0)

    return start_night_time <= now or now <= end_night_time


async def get_all_critical_hosts_info():
    """Get information about all critical hosts."""

    parser = GetCriticalHostNagios(
        url=env.str("URL_NAGIOS"),
        login=env.str("LOGIN_NAGIOS"),
        passwd=env.str("PASSWD_NAGIOS"),
    )

    return await parser.get_all_critical_hosts()


async def billing() -> BillingUserData:
    bill = BillingUserData(
        url=env.str("URL_BILLING"),
        login=env.str("LOGIN_BILLING"),
        passwd=env.str("PASSWD_BILLING"),
    )
    return bill


def userside():
    auth = UsersideWebDataFetcher(
        base_url=env.str("URL_USERSIDE"),
        login=env.str("LOGIN_USERSIDE"),
        password=env.str("PASSWD_USERSIDE"),
    )
    return auth


async def request_processing(url, payload: dict, file: dict = None) -> bool:
    """Send a request to the server and return True if successful"""

    with userside() as data_fetcher:
        if not data_fetcher.authenticate():
            return False

        return data_fetcher.send_server_request(url, payload, file)


async def send_message_with_retry(
    message: types.Message | Dispatcher,
    text: str,
    chat_id: int | None = None,
    keyboard: types.InlineKeyboardMarkup | None = None,
):
    """
    Send the message, and if it's too long,
    split and send as separate messages.

    :param message: The message object that triggered the function.
    :param text: The text of the message to be sent.
    :param keyboard: (Optional) The inline keyboard to be sent with the message.
    :param chat_id: (Optional) The ID of the chat to send the message to.
    """

    try:
        if chat_id:
            await message.bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_notification=is_night_time(),
                reply_markup=keyboard,
            )
        else:
            await message.answer(
                text=text,
                disable_notification=is_night_time(),
                reply_markup=keyboard,
            )
    except MessageIsTooLong:
        # Extra long message > 4096 characters
        parts = [text[i : i + 4096] for i in range(0, len(text), 4096)]

        # Sending each part as a separate message
        for part in parts:
            if chat_id:
                await message.bot.send_message(
                    chat_id=chat_id,
                    text=part,
                    disable_notification=is_night_time(),
                )
            else:
                await message.answer(
                    text=part,
                    disable_notification=is_night_time(),
                )

        logger.info(
            "Extra long message (%s) was split into %s messages.",
            len(text),
            len(parts),
        )


async def remove_html_tags(input_string):
    """
    Removes HTML tags from the input string and performs additional replacements.
    """

    # Replace <br> with newline (\n)
    modified_text = input_string.replace("<br>", "\n")

    # Replace &nbsp; with space
    modified_text = modified_text.replace("&nbsp;", " ")

    # Remove remaining HTML tags
    clean_text = re.sub(r"<[^>]*>", "", modified_text)

    return clean_text


async def set_locale(language: str = None) -> None:
    """Set the locale for date localization based on the chosen language."""

    lang_map = {
        "en": "en_US.UTF-8",
        "uk": "uk_UA.UTF-8",
        "de": "de_DE.UTF-8",
    }
    default_language = "en_US.UTF-8"
    try:
        locale.setlocale(
            locale.LC_ALL, lang_map.get(language, default_language)
        )
    except locale.Error as e:
        locale.setlocale(locale.LC_ALL, default_language)
        logger.error("Invalid or unsupported language: %s", e)


async def find_phone_number(text: str) -> list:
    """The function accepts text and finds phone numbers in the text"""
    phone_numbers = re.findall(
        r"(?:(?:\+|0{1,2})\d{1,3}[- ]?)?(?:\(\d{1,4}\)|\d{2,3})[- ]?\d{3}[- ]?\d{2,3}[- ]?\d{2,3}",
        text,
    )
    return phone_numbers


async def format_phone_numbers(phone: str) -> str:
    """
    The function accepts phone and formats them to standard +380XXXXXXXXX.

    Args:
    - phone (str): Text phone numbers.

    Returns:
    - str: Phone numbers in the format +380XXXXXXXXX.
    """
    if phone.startswith("+") and len(phone) >= 13:
        return f"📱 {phone}"

    digits = re.sub(r"\D", "", phone)  # remove all characters except numbers
    formatted_phone = f"☎ +380{digits[-9:]}"

    return formatted_phone


async def replacing_phone_numbers_in_text(text: str) -> str:
    """
    Replaces phone numbers in the text with their formatted counterparts.

    Args:
        - text (str): The input text where phone numbers will be replaced.

    Returns:
        str: The text with replaced phone numbers.
    """

    if phone_numbers := await find_phone_number(text):
        formatted_phone_number = [
            await format_phone_numbers(phone) for phone in phone_numbers
        ]

        for old_phone, new_phone in zip(phone_numbers, formatted_phone_number):
            text = text.replace(old_phone, new_phone)

    return text


def parse_address(address: str) -> dict | None:
    """
    Parses an address string and returns a dictionary with the parts separated.

    :param address: Address line in the format "City, Street (vul.), House number"
    :return: Dictionary with parts of the address (city, street, name, prefix, house number)
    """

    if not address:
        return None

    def extract_number(number_string: str) -> str | None:
        """
        Extracts a number with optional fraction and
        alphanumeric characters from the input string.
        """
        match = re.search(r"\b(\d+(?:/\d+)?\w?)\b", number_string)
        return match.group(1) if match else None

    def extract_street_info(location_str: str) -> tuple[str, str]:
        """
        Extracts street name and prefix from the location string.
        """
        location_parts = location_str.split(" (")
        street_parts = location_parts[0].split(" &#047; ")
        street_name = (
            street_parts[1].strip()
            if len(street_parts) > 1
            else street_parts[0].strip()
        )
        street_prefix = (
            location_parts[-1][:-1].strip()
            if location_parts[-1].endswith(")")
            else ""
        )
        return street_name, street_prefix

    # Splitting a string into parts
    city, location, number_part = map(str.strip, address.split(", "))

    # Extracting street name and prefix
    name, prefix = extract_street_info(location)

    # Extracting building number
    building_number = extract_number(number_part.split(" ")[0])

    result = {
        "city": city,
        "street": name,
        "prefix": prefix,
        "building_number": building_number,
    }
    return result
