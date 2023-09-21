import asyncio
from datetime import datetime, timedelta

from utils.db.data_process import DataBaseOperations
from utils.log import logger


class DutyScheduler:
    """DutyScheduler manages duty scheduling for a list of persons."""

    DAYS_BETWEEN_SHIFTS = 7

    def __init__(self, persons: tuple):
        self.persons = persons
        self.logger = logger

    async def determine_duty_person(self, date: datetime) -> str:
        """Determine the person on duty for a given date."""
        if not self.persons:
            raise ValueError("No persons on duty")

        days_difference = (date - datetime(2023, 9, 23)).days
        person_index = (
            days_difference // self.DAYS_BETWEEN_SHIFTS % len(self.persons)
        )
        return self.persons[person_index]

    async def get_duty_day_info(self, date=None):
        """Get duty day information for a specific date or the current date."""

        parsed_date = (
            datetime.strptime(date, "%d.%m.%Y") if date else datetime.now()
        )
        day_of_week = parsed_date.weekday()
        start_of_week = parsed_date - timedelta(days=day_of_week)
        saturday = start_of_week + timedelta(days=5)
        sunday = start_of_week + timedelta(days=6)
        person_name = await self.determine_duty_person(saturday)
        weekend = [
            day.strftime("%A: %d %B %Y").title() for day in (saturday, sunday)
        ]

        result = {"day_off": weekend, "person_duty": person_name}
        return result


async def main():

    people = await DataBaseOperations().get_users_from_db(duty_only=True)
    if people:
        persons = tuple(dict(person).get("full_name") for person in people)
        print(persons)
        scheduler = DutyScheduler(persons=persons)
        duty_info = await scheduler.get_duty_day_info("28.10.2023")
        weekends = ", ".join(duty_info["day_off"])
        print(duty_info["person_duty"], weekends)


if __name__ == "__main__":
    asyncio.run(main())
