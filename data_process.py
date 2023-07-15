import logging
import sqlite3


class DataBaseOperations:
    """Operations with the SQLite database"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._connect_sql = sqlite3.connect("monitor.db")
        self._cursor = self._connect_sql.cursor()

    async def write_all_hosts_to_db(self, hosts: list[tuple[str]]) -> None:
        """Write the host names to the database"""

        with self._connect_sql:
            self._cursor.executemany(
                "INSERT OR IGNORE INTO failed_resources (host_name) VALUES (?)",
                hosts,
            )
            self._connect_sql.commit()

    async def write_one_host_to_db(self, host: tuple[str]) -> None:
        """Write a single host name to the database"""
        await self.write_all_hosts_to_db([host])

    async def get_all_hosts_from_db(self) -> list[tuple[str]]:
        """Get the host names from the database"""

        with self._connect_sql:
            self._cursor.execute("SELECT host_name FROM failed_resources")
        return self._cursor.fetchall()

    async def delete_one_host_from_db(self, host: tuple[str]) -> None:
        """Delete a single host from the database"""

        with self._connect_sql:
            self._cursor.execute(
                "DELETE FROM failed_resources WHERE host_name = (?)", host)
            self._connect_sql.commit()

    async def check_hosts_from_db(self, hosts: list[tuple[str]]) -> list[str]:
        """Check the host names from the database"""

        hosts_in_db = await self.get_all_hosts_from_db()
        # Find the difference between the input hosts and database hosts
        diff_hosts = set(hosts) ^ set(hosts_in_db)
        result = []

        for host in diff_hosts:
            host_status = "🔴" if host not in hosts_in_db else "🟢"
            result.append("".join(f"{host_status} {i}" for i in host))
            if host not in hosts_in_db:
                await self.write_one_host_to_db(host)
            else:
                await self.delete_one_host_from_db(host)

        return result
