import asyncio
from environs import Env
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data_process import DataBaseOperations
from nagios import GetCriticalHostNagios
from send import NagiosTelegramNotifier

# Read environment variables
env = Env()
env.read_env()

# Create an asyncio event loop
loop = asyncio.get_event_loop()


async def main():
    """Main function"""

    # Instantiate the Nagios parser
    parser = GetCriticalHostNagios(
        login=env.str("LOGIN_NAGIOS"), passwd=env.str("PASSWD_NAGIOS"))

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


# Create a scheduler
scheduler = AsyncIOScheduler(event_loop=loop, timezone="Europe/Kiev")

# Add the main function as a scheduled job
scheduler.add_job(main, 'interval', seconds=10)  # Execute every 10 minutes

# Start the scheduler
scheduler.start()

# Run the event loop indefinitely
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    scheduler.shutdown()
    loop.close()
