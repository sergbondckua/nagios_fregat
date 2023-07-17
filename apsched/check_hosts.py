from aiogram.utils.markdown import text

import const_texts as ct
from loader import dp, env, is_silent
from utils.db.data_process import DataBaseOperations
from utils.nagios import GetCriticalHostNagios
from utils.log import logger


async def monitoring():
    """Monitoring the network host"""

    # Instantiate the Nagios parser
    username = env.str("LOGIN_NAGIOS")
    password = env.str("PASSWD_NAGIOS")
    parser = GetCriticalHostNagios(login=username, passwd=password)

    # Get all critical hosts from Nagios
    hosts = await parser.get_all_critical_hosts()

    # Initialize the database operations
    db = DataBaseOperations()

    # Check hosts status from the database
    changed_hosts = await db.check_hosts_from_db(hosts)

    # Send in Telegram the list of checked hosts
    if changed_hosts:
        msg = text(
            ct.changed_hosts_status,
            "\n".join(changed_hosts),
            text(
                "----",
                f"👉 <a href='{ct.url_nagios}'>Nagios</a> | /nagios",
                sep="\n",
            ),
            sep="\n\n",
        )
        await dp.bot.send_message(
            chat_id=env.int("CHAT_SUPPORT_ID"),
            disable_notification=is_silent(),
            text=msg,
        )
    else:
        logger.info("The current status of the hosts has not changed")
