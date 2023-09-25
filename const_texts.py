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
    text("\t\t\t• Пересилатиму вам назначені на вас заявки по роботі.")
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
btn_cancel_send = text("Скасувати надсилання")
btn_add_photo = text("🖼 Додати фото")
btn_approve_send = text("✅ Відправити")
btn_cancel_comment = text("❌ Відмінити")
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
not_found_task_id = text(
    "🚫 Номер завдання не знайдено або помилка при введені."
)
# Usersider
no_data = text("😥 Ой, на даний момент інформація відсутня.")
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

# task_manager
send_task_msg = text(
    hbold("#️⃣ {} - {}"),
    text(
        "👤 Абонент:",
        hbold({}),
        hcode("/ab chk_{}"),
        sep=newline_margin,
    ),
    text(
        "📬 Адреса:",
        hbold({}),
        sep=newline_margin,
    ),
    text(
        text("✏️", hbold("Завдання:")),
        {},
        sep="\n" + newline_margin,
    ),
    text(
        "✍️ -----\n\n",
        hbold("Додати коментар: "),
        hcode("/add_cmt {}:"),
    ),
    sep="\n\n",
)
sent_success = text(
    "✅", hcode("/# {}"), " - Успішно відправлено -> " + hbold({})
)
sent_unsuccessful = text(
    "⛔️",
    hcode("/# {}"),
    " - НЕ відправлено\n",
    hbold("{} - Заблокував бота"),
)
assign_task_msg = text(
    text(hbold("#{} - {}"), {}, sep=newline_margin),
    hitalic("Оберіть адресата: 👇"),
    sep="\n\n",
)

# task_comment
done_task_comment = "Завдання виконано успішно!"
comment_msg = text(
    text({}, ":", sep=""),
    {},
    sep=newline_margin,
)
typical_comment = text(
    text({}, ":", sep=""),
    done_task_comment,
    sep=newline_margin,
)
write_comment = text(
    text("✍️", hbold("Напиши свій коментар до завдання #{}:\n")),
    hitalic("🔸 Не використовуй емодзі в коментарі."),
    hitalic(
        "🔸 Коментар із знаком '+', автоматично вставить",
        text(f"➖ {done_task_comment}"),
        sep=newline_margin,
    ),
    sep=newline_margin,
)
pre_send_comment = text(
    text("👀", hbold("Попередній перегляд Вашого коментаря:\n")),
    "➖➖➖",
    {},
    "➖➖➖",
    sep=newline_margin,
)
cancel_comment = text("Відправка коментаря скасована")
add_task_comment_msg = text(
    text(
        "🆗 Коментар для заявки",
        hlink(
            "#{title}",
            env.str("URL_USERSIDE")
            + "oper/journal.php?type=working&type2=show&code={code}",
        ),
        "додано: ",
    ),
    hitalic({}),
    sep=newline_margin + "\n",
)

# attach_photo
send_photo_to_task = text(
    "📸",
    hbold("Надішліть фотографію до завдання #") + hcode({}),
)
add_photo_or_cancel = text(
    text("⚠️", hbold("Наступним повідомленням має бути фото!")),
    "🖼 Додайте фотографію або скасуйте надсилання!",
    sep=newline_margin,
)
cancel_send_done = text("☑️ Відправка фото скасовано.")
add_task_photo_msg = text(
    text("➕ Фото для заявки", hbold("#") + hcode({}), "додано: "),
    hitalic({}),
    sep=newline_margin,
)

# USER MANAGER
not_found_users = text("В системі немає жодного зареєстрованого користувача.")
user_menu_text = text(
    hbold("Зміна параметрів для:"),
    "👷‍♂️ {}",
    text(
        hbold("Поточні параметри:"),
        "Виконавець: {}",
        "Чергувальник: {}",
        sep=newline_margin,
    ),
    sep="\n\n",
)
btn_implementer = "✔️ Виконавець"
btn_not_implementer = "➖ Не виконавець"
btn_duty_man = "✔️ Чергувальник"
btn_not_duty_man = "➖ Не чергувальник"
btn_delete_user = "➰ Видалити"
