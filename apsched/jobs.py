from apsched.check_hosts import monitoring
from apsched.duty import set_and_notify_duty
from apsched.storm_warning import notice_of_possible_thunderstorms
from loader import scheduler, env


async def start_scheduler() -> None:
    """Start scheduler and add tasks apscheduler"""

    # Monitors the status of hosts
    scheduler.add_job(monitoring, "interval", seconds=90)

    # Monitoring possible thunderstorms
    if env.bool("IS_REPORT_STORM"):
        scheduler.add_job(
            func=notice_of_possible_thunderstorms,
            trigger="cron",
            minute=0,
            hour=8,
            month="3-11",
            day_of_week="mon, wed, fri",
        )

    # Assign weekend schedules duty
    scheduler.add_job(
        func=set_and_notify_duty,
        trigger="cron",
        minute=3,
        hour=19,
        day_of_week="mon, wed",
    )

    # Start the scheduler
    scheduler.start()
