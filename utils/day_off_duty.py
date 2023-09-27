from datetime import datetime, timedelta

from utils.db.data_process import DataBaseOperations
from utils.log import logger


class DutyScheduler:
    """DutyScheduler manages duty scheduling for a list of persons."""

    DAYS_BETWEEN_SHIFTS = 7

    def __init__(self):
        self.logger = logger
        self.db = DataBaseOperations()

    async def assign_duty(self):
        """
        Assign duty to employees in a round-robin fashion.

        This function selects the next available employee for duty and updates their status.
        It works in a round-robin manner, ensuring that each employee is assigned duty in turn.
        """

        # Select users who can be on duty
        query_duty_users = await self.db.get_users_from_db(**{"duty": True})
        available_duty_users = [dict(i) for i in query_duty_users]

        if available_duty_users:
            # Get the current duty user
            query_current_duty = await self.db.get_users_from_db(
                **{"is_duty": True}
            )
            current_duty_user = query_current_duty.fetchone()

            if current_duty_user:
                # Find the index of the current duty employee in the available users list
                current_index = next(
                    (
                        i
                        for i, emp in enumerate(available_duty_users)
                        if dict(emp)["user_id"]
                        == dict(current_duty_user)["user_id"]
                    ),
                    None,
                )
            else:
                current_index = -1

            # Calculate the index of the next user for duty
            next_index = (current_index + 1) % len(list(available_duty_users))
            next_duty_user = available_duty_users[next_index]

            if current_duty_user:
                # Update the status of the current duty user
                await self.db.update_user_to_db(
                    current_duty_user["user_id"], **{"is_duty": False}
                )

            # Update the status of the next duty user
            await self.db.update_user_to_db(
                next_duty_user["user_id"], **{"is_duty": True}
            )

            return next_duty_user

        self.logger.warning("None of the users are assigned to take turns.")
        return None

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
        person_name = await self.assign_duty()
        weekend = [
            day.strftime("%A: %d %B %Y").title() for day in (saturday, sunday)
        ]

        result = (
            {"user_duty": person_name, "weekend": weekend}
            if person_name
            else None
        )

        return result
