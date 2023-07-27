import asyncio
from datetime import datetime

import pygismeteo

from loader import dp, env, is_night_time
from utils.log import logger


async def get_weather_forecast() -> list[tuple[str, str]]:
    """
        Get the weather forecast for a specific location.

        Returns:
            List of tuples, where each tuple contains the date
            and the full weather description for that date.
    """

    gm = pygismeteo.Gismeteo(lang="ua")
    forecast = gm.step24.by_id(id=env.int("GM_CITY_ID"), days=3)

    return [
        (
            datetime.fromtimestamp(entry.date.unix).strftime("%d.%m.%Y"),
            entry.description.full,
        )
        for entry in forecast
        if not entry.storm
    ]


async def notice_of_possible_thunderstorms() -> None:
    """
        Check the weather forecast and send a notification
        in case of possible thunderstorms.
    """

    weather_forecast = await get_weather_forecast()
    if weather_forecast:
        message = "".join(
            f"{date}: {description}\n" for date, description in weather_forecast
        )
        await dp.bot.send_message(
            chat_id=env.int("CHAT_SUPPORT_ID"),
            disable_notification=is_night_time(),
            text=message,
        )
    else:
        logger.info("Thunderstorms are not expected")


if __name__ == "__main__":
    asyncio.run(notice_of_possible_thunderstorms())
