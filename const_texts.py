from aiogram.utils.markdown import text, hbold, hcode

all_down_hosts = text(hbold("Всі непрацюючі адреси:"))
changed_hosts_status = text(hbold("Адреси статус яких змінився:"))
url_nagios = text(
    "http://193.108.248.20/nagios/cgi-bin/status.cgi?host=all&servicestatustypes=16"
)
start_text = text(
    hbold("Hello!"), "I'm Fregi!",
    hcode("Powered by Serhii Bondarenko aka Ninja."),
    sep="\n",
)
all_ok = text("Все добре! Не знайдено проблем")
