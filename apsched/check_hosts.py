from datetime import timedelta

import const_texts as ct
from loader import dp, env
from utils.db.data_process import DataBaseOperations
from utils.log import logger
from utils.misc import (
    get_all_critical_hosts_info,
    send_message_with_retry,
)


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

        await send_message_with_retry(
            message=dp,
            text=ct.changed_hosts_status.format(changed_hosts_str),
            chat_id=env.int("CHAT_SUPPORT_ID"),
        )
    else:
        logger.info("The current status of the hosts has not changed")
