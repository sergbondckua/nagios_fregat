from aiogram.utils.markdown import text, hbold, hcode, hlink, hitalic
from loader import env

all_down_hosts = text(
    hbold("Всі непрацюючі адреси: ({})"),
    "{}",
    sep="\n\n",
)
host_detail_name_row = text(
    "🔻 • " + hbold("{}"),
    "|_ " + hcode("{}"),
    "|_ " + hcode("{}"),
    sep="\n\t\t\t\t\t\t\t",
)
host_name_row = text(
    "🟥 • {}",
)
storm_report = text(
    hbold("🌩 Попередження про ймовірні грози."),
    "{}",
    text("----", hlink("Gismeteo", "https://meteofor.com.ua/"), sep="\n"),
    sep="\n\n\t",
)
storm_data_row = text(
    "• ",
    hbold("{}"),
    "{}",
)
url_nagios = text(
    env.str("URL_NAGIOS") + "?host=all&servicestatustypes=16&limit=0"
)

changed_hosts_status = text(
    hbold("Адреси статус яких змінився:"),
    "{}",
    text(
        "----",
        hlink("Nagios", url_nagios) + " | /nagios",
        sep="\n",
    ),
    sep="\n\n",
)

start_text = text(
    hbold("Привіт!"),
    "Я бот 🤖 {}",
    "\t\t\t• Я готовий допомагати 24/7 вам контролювати стан хостів (адрес) і повідомляти "
    "про будь-які зміни у їх роботі.",
    text(
        "\t\t\t• Спостерігатиму за погодую та відразу повідомлю в чат/канал про ймовірні грози"
    )
    if env.bool("IS_REPORT_STORM")
    else "\t\t\t• Можу повідомляти про ймовірні грози, але ця опція вимкнена в налаштуваннях"
    + hcode(".env"),
    "🚀 Залишайтесь на зв'язку і нехай ваші хости завжди будуть під контролем!",
    sep="\n\n\t",
)
help_text = text(
    hbold("Функціонал:"),
    text(
        text(
            "\t\t\t• Бот періодично, кожні 90 секунд, виконуватиме запит до веб-додатка",
            hlink("Nagios", env.str("URL_NAGIOS")) + ".",
        ),
        text(
            "\t\t\t• Якщо який-небудь хост (адреса) не працює протягом",
            text(env.str("MAX_DOWN_TIME_MINUTES")),
            "хвилин або більше, лише тоді бот вважатиме, що існує проблема з цим хостом (адресою). ",
        ),
        text(
            "\t\t\t• Після цього, бот надсилатиме відповідне повідомлення до Чату/Каналу.\n",
            "\t\t\t• Всі адреси, які перебувають у стані неробочих менше ніж",
            text(env.str("MAX_DOWN_TIME_MINUTES")),
            "хвилин, будуть ігноруватися.",
        ),
        sep="\n",
    ),
    hbold("Команди:"),
    text(
        hbold("\t\t\t/nagios"),
        hitalic("- Отримати всі непрацюючі хости на поточний момент."),
    ),
    sep="\n\n",
)
btn_detail = "🗂 Докладно"
all_ok = text("Все добре! Не знайдено проблем")
