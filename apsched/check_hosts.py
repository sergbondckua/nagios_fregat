from datetime import timedelta

import const_texts as ct
from loader import dp, env, is_night_time, get_all_critical_hosts_info
from utils.db.data_process import DataBaseOperations
from utils.log import logger


async def monitoring():
    """Monitoring the network host"""

    # Get all critical hosts from Nagios
    critical_hosts = await get_all_critical_hosts_info()

    # Filter 'hosts' list based on timedelta condition,
    # and create a set of host names.
    critical_hosts_delta = [
        (i[0],)
        for i in critical_hosts
        if i[1] >= timedelta(minutes=env.int("MAX_DOWN_TIME_MINUTES"))
    ]

    # Initialize the database operations
    db = DataBaseOperations()

    # Check hosts status from the database
    changed_hosts = await db.check_hosts_from_db(critical_hosts_delta)

    # Send in Telegram the list of checked hosts
    if changed_hosts:
        # Convert the list of changed hosts to a formatted string
        changed_hosts_str = "\n".join(changed_hosts)

        await dp.bot.send_message(
            chat_id=env.int("CHAT_SUPPORT_ID"),
            disable_notification=is_night_time(),
            text=ct.changed_hosts_status.format(changed_hosts_str),
        )
    else:
        logger.info("The current status of the hosts has not changed")
