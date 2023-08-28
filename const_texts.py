from aiogram.utils.markdown import text, hbold, hcode, hlink, hitalic
from loader import env

newline_margin = "\n\t\t\t\t"
margin = "\t\t\t"
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
    ),
    text(
        "\t\t\t• Пересилатиму вам назначені на вас заявки по роботі."
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
            margin,
            "• Бот періодично, кожні 90 секунд, виконуватиме запит до веб-додатка",
            hlink("Nagios", env.str("URL_NAGIOS")) + ".",
        ),
        text(
            margin,
            "• Якщо який-небудь хост (адреса) не працює протягом",
            text(env.str("MAX_DOWN_TIME_MINUTES")),
            "хвилин або більше, лише тоді бот вважатиме, що існує проблема з цим хостом (адресою). ",
        ),
        text(
            margin,
            "• Після цього, бот надсилатиме відповідне повідомлення до Чату/Каналу.\n",
            margin,
            "• Всі адреси, які перебувають у стані неробочих менше ніж",
            text(env.str("MAX_DOWN_TIME_MINUTES")),
            "хвилин, будуть ігноруватися.",
        ),
        sep="\n",
    ),
    hbold("Команди:"),
    text(
        hbold(margin + "/nagios"),
        hitalic("- Отримати всі непрацюючі хости на поточний момент."),
    ),
    text(
        hbold(margin + "/abon chk_example"),
        hbold(margin + "/abon Lastname Firstname"),
        hitalic("- Отримати меню білінг-сервісів абонента."),
    ),
    sep="\n\n",
)
btn_detail = text("🗂", "Докладно")
all_ok = text("Все добре! Не знайдено проблем")
credentials_detail = text(
    hbold("Бланк налаштувань абонента:"),
    "{}",
    sep="\n\n",
)
sessions_text = text(
    hbold("{} － {}"),
    text(hcode({}), "{}", hcode({}), sep=newline_margin),
    sep=newline_margin,
)
not_found_session = text("За 3 останні місяці сесій не знайдено.")
selected_user_text = text(
    text("Абонент:", hbold({})),
    "Оберіть і отримайте потрібну інформацію.",
    sep="\n",
)
response_users_text = text(
    text(
        "За вашим запитом:",
        hbold("{}"),
        sep=newline_margin,
    ),
    "Отримані результати:",
    "{}",
    sep="\n\n",
)
results_response_users = text(
    text(hbold("{}."), hlink("{title}", "{url}"), ":"),
    "{}",
    "{}",
    sep=newline_margin,
)
btn_close = text("✖️", "Прибрати")
btn_sessions = text("Сесії")
btn_blank = text("Облікові дані")
btn_balance = text("Баланс")
btn_diagnosis = text("Діагностика")
btn_access = text("Розташування/Доступ")
btn_show_mac = text("Show Mac")
btn_show_errors = text("Show Errors")
btn_cable_test = text("Cable test")
user_not_found = text("🚷", "Результату за запитом ({}) немає.")
correct_abon_command = text("Некоректний формат команди.")
timeout_error = text(
    "⛔️", "Перевищено інтервал очікування. Збій у роботі сервера."
)
require_group_member_text = text(
    "🚫",
    "{}, дана команда та функціонал Вам не доступні. Ви не є членом потрібної групи.",
)
not_authorized_userside = text("Неуспішна авторизація в Userside")
not_found_task_id = text("🚫 Номер завдання не знайдено або помилка при введені.")
access_decsriptions = text(
    text(hbold("Адреса: "), {}),
    text(hbold("Світч: "), {}),
    text(hbold("Порт абон-та: "), {}, "({})"),
    text(hbold("Опис доступу: "), {}, sep="\n"),
    sep="\n\n",
)

telnet_menu_msg = text(
    text(hbold({}) + ":", hbold({})),
    text("Світч: ", hlink("{title}", "{url}"), "Порт: ", hbold({})),
    text("Адреса: ", hbold({})),
    text(hcode({})),
    sep="\n\n",
)
telnet_menu_diagnostics = text(
    text(hbold("Діагностика: "), {}),
    text(
        "🚨 Увага! ",
        hitalic(
            "⚠️ D-Link DES-xxx-xx/C1 - При `cable test` комбо-портів є ризик, що вимкнуться ВСІ комбо-порти.",
            "⚠️ На деяких комутаторах при `cable test` вимикається порт.",
            "️️⚠️ По можливості не використовуйте кабельну діагностику на комбо-портах.",
            "️⚠️ Edge-corE вимикає порт, коли робить кабельну діагностику, це може бути "
            "причиною переривання сесії у абон-та, та помилок на порту.",
            sep="\n",
        ),
        sep="\n",
    ),
    sep="\n\n",
)
send_task_msg = text(
    hbold("#️⃣ {} - {}"),
    text(
        "👤 Абонент: ",
        hbold({}),
        hcode("/ab chk_{}"),
        sep=newline_margin,
    ),
    "📬 Адреса завдання: " + hbold({}),
    text(
        text("✏️", "Опис: "),
        "{}".strip(),
        sep="\n\n",
    ),
    text(
        "✍️ -----\n\n",
        "Додати коментар: ",
        hcode("/add_cmt {}:"),
    ),
    sep="\n\n",
)
sent_success = text(
    "✅", hcode("/# {}"), " - Успішно відправлено -> " + hbold({})
)
sent_unsuccessful = text(
    "⛔️", hcode("/# {}"),
    " - НЕ відправлено\n",
    hbold("{} - Заблокував бота"),
)
assign_task_msg = text(
    text(hbold("#{} - {}"), {}, sep=newline_margin),
    hitalic("Оберіть адресата: 👇"),
    sep="\n\n",
)
add_task_comment_msg = text(
    text("🆗 Коментар для заявки", hbold("#{}"), "додано: "),
    hitalic({}),
    sep=newline_margin + "\n",
)
typical_comment = text("Завдання виконано успішно!")
