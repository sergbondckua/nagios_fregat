from aiogram.utils.markdown import text, hbold, hcode
from loader import env

all_down_hosts = text(hbold("Всі непрацюючі адреси:"))
changed_hosts_status = text(hbold("Адреси статус яких змінився:"))
url_nagios = text(
    env.str("URL_NAGIOS") + "?host=all&servicestatustypes=16&limit=0"
)

start_text = text(
    hbold("Привіт!"), "Я бот 🤖 %s",
    hcode("Powered by Serhii Bondarenko aka Ninja."),
    sep="\n",
)
all_ok = text("Все добре! Не знайдено проблем")
