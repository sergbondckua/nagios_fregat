import locale
from datetime import datetime, timedelta

from utils.log import logger


def determine_duty_person(date: datetime) -> str:
    people = ["Ninja", "Andrej"]
    start_date = datetime(2023, 9, 23)
    days_between_shifts = 7
    days_difference = (date - start_date).days
    person_index = days_difference // days_between_shifts % len(people)
    return people[person_index]


def get_duty_day_info(date=None, language: str = "en") -> dict:
    lang_map = {
        "en": "en_US",
        "ukr": "ukr_UA",
        "de": "de_DE",
    }

    try:
        locale.setlocale(locale.LC_ALL, lang_map[language])
    except locale.Error as e:
        locale.setlocale(locale.LC_ALL, "en_US")
        logger.error("Invalid language: %s", e)
    except KeyError as e:
        locale.setlocale(locale.LC_ALL, "en_US")
        logger.error("Not found language: %s", e)

    date = datetime.strptime(date, "%d.%m.%Y") if date else datetime.now()
    day_of_week = date.weekday()
    start_of_week = date - timedelta(days=day_of_week)
    saturday, sunday = start_of_week + timedelta(
        days=5
    ), start_of_week + timedelta(days=6)
    person_name = determine_duty_person(saturday)

    result = {"day_off": [saturday, sunday], "person_duty": person_name}

    return result


if __name__ == "__main__":
    duty_info = get_duty_day_info(language="uk")
    weekend = ", ".join(
        day.strftime("%A: %d %B %Y").title() for day in duty_info["day_off"]
    )
    print(duty_info["person_duty"], weekend)
