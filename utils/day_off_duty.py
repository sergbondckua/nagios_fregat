import locale
import sys
from datetime import datetime, timedelta


def set_locale(language="en"):
    lang = {
        "en": {
            "name_locale": "en_US",
        },
        "ukr": {
            "name_locale": "uk_UA",
        },
        "de": {
            "name_locale": "de_DE",
        },
    }
    name_locale = lang.get(language)

    # Задаем локаль для вывода даты на UKR языке в зависимости какая ОС
    if sys.platform == "linux":
        locale.setlocale(
            locale.LC_ALL, name_locale.get("name_locale")
        )  # Ubuntu
    elif sys.platform == "win32":
        locale.setlocale(locale.LC_ALL, language)  # Windows
    elif sys.platform == "darwin":
        locale.setlocale(locale.LC_ALL, name_locale.get("name_locale"))  # MacOS


# Особи, які чергують
people = ["Ninja", "Andrej"]

# Початкова дата вихідного та кількість днів між чергуваннями
start_date = datetime(
    2023, 9, 23
)  # Початкова дата (розпочніть з першого вихідного)
days_between_shifts = 7  # Кількість днів між чергуваннями


# Функція для визначення, хто чергує в певну дату
def determine_person_for_date(date=datetime.now(), language=None):
    if language:
        set_locale(language)

    days_difference = (date - start_date).days
    person_index = days_difference // days_between_shifts % len(people)
    return people[person_index]


# Введіть дату вихідного у форматі рік, місяць, день
target_date = datetime(2023, 12, 10)

# Знайти день тижня для вказаної дати (0 - понеділок, 6 - неділя)
day_of_week = target_date.weekday()

# Визначити початок тижня (понеділок) та вихідні дні тижня (субота, неділя)
start_of_week = target_date - timedelta(days=day_of_week)
saturday, sunday = start_of_week + timedelta(days=5), start_of_week + timedelta(
    days=6
)

# Визначте, хто чергує у введену дату
result_person = determine_person_for_date(saturday, "ukr")

# Виведіть результат
print(f"{saturday.strftime('%d %B %Y, %A').title()} чергує: {result_person}")
