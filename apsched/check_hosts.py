import const_texts as ct
from loader import dp, env, is_night_time
from utils.db.data_process import DataBaseOperations
from utils.nagios import GetCriticalHostNagios
from utils.log import logger


async def monitoring():
    """Monitoring the network host"""

    # Instantiate the Nagios parser
    nagios_parser = GetCriticalHostNagios(
        url=env.str("URL_NAGIOS"),
        login=env.str("LOGIN_NAGIOS"),
        passwd=env.str("PASSWD_NAGIOS"),
    )

    # Get all critical hosts from Nagios
    critical_hosts = await nagios_parser.get_all_critical_hosts()

    # Initialize the database operations
    db = DataBaseOperations()

    # Check hosts status from the database
    changed_hosts = await db.check_hosts_from_db(critical_hosts)

    # Send in Telegram the list of checked hosts
    if changed_hosts:

        # Convert the list of changed hosts to a formatted string
        changed_hosts_str = "\n".join(changed_hosts)

        await dp.bot.send_message(
            chat_id=env.int("CHAT_SUPPORT_ID"),
            disable_notification=is_night_time(),
            text=ct.changed_hosts_status % (changed_hosts_str,),
        )
    else:
        logger.info("The current status of the hosts has not changed")
