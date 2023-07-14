import asyncio
import logging
import sqlite3

from environs import Env

from nagios import GetCriticalHostNagios

env = Env()
env.read_env()


class DataBaseOperations:
    """Operations with the SQLite database"""

    _connect_sql = sqlite3.connect("monitor.db")
    _cursor = _connect_sql.cursor()

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def write_all_hosts_to_db(self, hosts):
        """Write the host names to the database"""
        with self._connect_sql:
            self._cursor.executemany(
                """
                INSERT OR IGNORE INTO failed_resources (host_name)VALUES (?)
                """,
                hosts,
            )
            self._connect_sql.commit()

    async def write_one_host_to_db(self, host):
        """Write the host names to the database"""
        with self._connect_sql:
            self._cursor.execute(
                """
                INSERT OR IGNORE INTO failed_resources (host_name)VALUES (?)
                """,
                host,
            )
            self._connect_sql.commit()

    async def get_all_hosts_from_db(self):
        """Get the host names from the database"""
        with self._connect_sql:
            self._cursor.execute(
                """
                SELECT host_name FROM failed_resources
                """
            )
        return self._cursor.fetchall()

    async def delete_one_host_from_db(self, host):
        """Delete the host from the database"""
        with self._connect_sql:
            self._cursor.execute(
                """
                DELETE FROM failed_resources WHERE host_name = (?)
                """,
                host,
            )
            self._connect_sql.commit()

    async def check_hosts_from_db(self, hosts):
        """Check the host names from the database"""

        for host in hosts:
            if host not in await self.get_all_hosts_from_db():
                print(host)
                await self.write_one_host_to_db(host)
            else:
                print(host)
                await self.delete_one_host_from_db(host)


async def main():
    parser = GetCriticalHostNagios(
        login=env.str("LOGIN_NAGIOS"), passwd=env.str("PASSWD_NAGIOS"))
    hosts = await parser.get_all_hosts()
    db = DataBaseOperations()
    all_hosts = await db.get_all_hosts_from_db()
    # print(hosts, all_hosts, sep='\n')
    await db.check_hosts_from_db(hosts)
    # await db.write_all_hosts_to_db(hosts)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
