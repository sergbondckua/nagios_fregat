from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Актувуйте бота"),
            types.BotCommand("help", "Довідка"),
            types.BotCommand("nagios", "Отримати всі непрацюючі хости"),
            types.BotCommand("myid", "Ваші ID дані"),
        ]
    )
