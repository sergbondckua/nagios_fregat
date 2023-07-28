from datetime import datetime, time

from pytz import timezone

from loader import env
from utils.nagios import GetCriticalHostNagios


def is_night_time():
    """
    Checks if the current time is within the night hours.

    Returns:
        bool: True if the current time is during the night, False otherwise.
    """

    now = datetime.now(tz=timezone(env.str("TZ"))).time()
    start_night_time = time(22, 0)
    end_night_time = time(7, 0)

    return start_night_time <= now or now <= end_night_time


async def get_all_critical_hosts_info():
    """Get information about all critical hosts."""

    parser = GetCriticalHostNagios(
        url=env.str("URL_NAGIOS"),
        login=env.str("LOGIN_NAGIOS"),
        passwd=env.str("PASSWD_NAGIOS"),
    )

    return await parser.get_all_critical_hosts()
