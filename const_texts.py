from aiogram.utils.markdown import text, hbold, hcode
from loader import env

all_down_hosts = text(
            hbold("Всі непрацюючі адреси: (%d)"),
            "%s",
            sep="\n\n",
        )

url_nagios = text(
    env.str("URL_NAGIOS") + "?host=all&servicestatustypes=16&limit=0"
)

changed_hosts_status = text(
            hbold("Адреси статус яких змінився:"),
            "%s",
            text(
                "----",
                f"👉 <a href='{url_nagios}'>Nagios</a> | /nagios",
                sep="\n",
            ),
            sep="\n\n",
        )

start_text = text(
    hbold("Привіт!"), "Я бот 🤖 %s",
    "Я готовий допомагати 24/7 вам контролювати стан хостів (адрес) і повідомляти "
    "про будь-які зміни у їх роботі. Коли хост перестає працювати, "
    "я сповіщу в відповідний чат/канал, щоб ви могли прийняти необхідні заходи. "
    "Та ж сама історія стосується і відновлення роботи хоста — "
    "в чат/канал також отримаєте повідомлення, якщо хост повернеться до нормального стану.",

    "Залишайтесь на зв'язку і нехай ваші хости завжди будуть під контролем!",

    "Приємного користування та успіхів у моніторингу ваших хостів! 🚀",
    hcode("Powered by Serhii Bondarenko aka Ninja."),
    sep="\n\n",
)

all_ok = text("Все добре! Не знайдено проблем")

