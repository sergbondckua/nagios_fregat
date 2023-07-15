import sqlite3

from environs import Env

from data_process import DataBaseOperations
from nagios import GetCriticalHostNagios
from send import NagiosTelegramNotifier

# Read environment variables
env = Env()
env.read_env()


async def monitoring():
    """Monitoring the network host"""

    # Instantiate the Nagios parser
    parser = GetCriticalHostNagios(
        login=env.str("LOGIN_NAGIOS"), passwd=env.str("PASSWD_NAGIOS")
    )

    # Get all critical hosts from Nagios
    hosts = await parser.get_all_critical_hosts()

    # Initialize the database operations
    db = DataBaseOperations()

    # Check hosts status from the database
    up_down_hosts = await db.check_hosts_from_db(hosts)

    # Initialize the Telegram notifier
    sender = NagiosTelegramNotifier(chat_id=env.int("CHAT_DEV_ID"))

    # Send in Telegram the list of checked hosts
    await sender.send_checked_hosts_list(up_down_hosts)
