from aiogram.utils.markdown import text, hbold, hcode, hlink, hitalic
from loader import env

all_down_hosts = text(
    hbold("Всі непрацюючі адреси: (%d)"),
    "%s",
    sep="\n\n",
)
host_detail_name_row = text(
    "🟥 • " + hbold("%s"),
    "|_ " + hcode("%s"),
    "|_ " + hcode("%s"),
    sep="\n\t\t\t\t\t\t\t",
)
host_name_row = text(
    "🟥 • %s",
)
storm_report = text(
    hbold("🌩 Попередження про ймовірні грози."),
    "%s",
    text("----", hlink("Gismeteo", "https://meteofor.com.ua/"), sep="\n"),
    sep="\n\n\t",
)
storm_data_row = text(
    "• ",
    hbold("%s:"),
    "%s",
)
url_nagios = text(env.str("URL_NAGIOS") + "?host=all&servicestatustypes=16&limit=0")

changed_hosts_status = text(
    hbold("Адреси статус яких змінився:"),
    "%s",
    text(
        "----",
        hlink("Nagios", url_nagios) + " | /nagios",
        sep="\n",
    ),
    sep="\n\n",
)

start_text = text(
    hbold("Привіт!"),
    "Я бот 🤖 %s",
    "Я готовий допомагати 24/7 вам контролювати стан хостів (адрес) і повідомляти "
    "про будь-які зміни у їх роботі. Коли хост перестає працювати, "
    "я сповіщу в відповідний чат/канал, щоб ви могли прийняти необхідні заходи. "
    "Та ж сама історія стосується і відновлення роботи хоста — "
    "в чат/канал також отримаєте повідомлення, якщо хост повернеться до нормального стану.",
    "Залишайтесь на зв'язку і нехай ваші хости завжди будуть під контролем!",
    "Приємного користування та успіхів у моніторингу ваших хостів! 🚀",
    sep="\n\n\t",
)
help_text = text(
    hbold("Функціонал:"),
    text(
        text(
            "   • Бот періодично, кожні 90 секунд, виконуватиме запит до веб-додатка",
            hlink("Nagios", env.str("URL_NAGIOS")) + ".",
        ),
        text(
            "   • Якщо який-небудь хост (адреса) не працює протягом",
            text(env.str("MAX_DOWN_TIME_MINUTES")),
            "хвилин або більше, лише тоді бот вважатиме, що існує проблема з цим хостом (адресою). ",
        ),
        text(
            "   • Після цього, бот надсилатиме відповідне повідомлення до Чату/Каналу.\n",
            "   • Всі адреси, які перебувають у стані неробочих менше ніж",
            text(env.str("MAX_DOWN_TIME_MINUTES")),
            "хвилин, будуть ігноруватися.",
        ),
        sep="\n",
    ),
    hbold("Команди:"),
    text(
        hbold("   /nagios"),
        hitalic("- Отримати всі непрацюючі хости на поточний момент."),
    ),
    sep="\n\n",
)
btn_detail = "ℹ️ Докладно"
all_ok = text("Все добре! Не знайдено проблем")
