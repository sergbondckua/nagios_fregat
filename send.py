import asyncio

from aiogram import Bot, Dispatcher, types

from nagios import GetCriticalHostNagios

bot = Bot(
    token="ererererere",
    parse_mode=types.ParseMode.HTML,
)
dp = Dispatcher(bot)


async def send_message_to_tg(hosts: list) -> None:
    """ Send a message to all hosts in the telegram chat """
    msg = "\n".join(f"🔴 {i}" for i in hosts)
    #  CHatTP
    #  -831686317
    await bot.send_message(chat_id=541696726, text=msg)


async def main():
    res = GetCriticalHostNagios(login="***", passwd="***")
    hosts = res.get_all_hosts()
    await send_message_to_tg(hosts)

if __name__ == '__main__':
    asyncio.run(main())

