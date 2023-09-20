import sqlite3

from aiogram import types

from loader import BASE_DIR
from utils.log import logger


class DataBaseOperations:
    """Operations with the SQLite database"""

    def __init__(self):
        self.logger = logger
        self._connect_sql = sqlite3.connect(BASE_DIR / "db.sqlite3")
        self._cursor = self._connect_sql.cursor()

    async def create_tables(self) -> None:
        """Create tables in the database if they don't already exist"""

        create_failed_resources_table = """
                CREATE TABLE IF NOT EXISTS failed_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host_name TEXT UNIQUE
                )
            """
        create_telegram_bot_users_table = """
                CREATE TABLE IF NOT EXISTS telegram_bot_users (
                    user_id INTEGER PRIMARY KEY UNIQUE,
                    username TEXT,
                    full_name TEXT,
                    staff BOOLEAN DEFAULT false,
                    duty BOOLEAN DEFAULT false
                )
            """
        add_column_duty = """
                ALTER TABLE telegram_bot_users
                ADD COLUMN duty BOOLEAN DEFAULT false;
            """

        with self._connect_sql:
            self._cursor.execute(create_failed_resources_table)
            self._cursor.execute(create_telegram_bot_users_table)
            try:
                self._cursor.execute(add_column_duty)
            except sqlite3.OperationalError as e:
                self.logger.error(e)
            self._connect_sql.commit()

    async def save_user_profile_to_db(self, user_data: types.User):
        """Save user profile information to the database"""

        query = """
                INSERT OR IGNORE INTO telegram_bot_users
                (user_id, username, full_name, staff)
                VALUES (?,?,?,?)
            """

        with self._connect_sql:
            self._cursor.execute(
                query,
                (user_data.id, user_data.username, user_data.full_name, False),
            )
            self._connect_sql.commit()

    async def update_user_profile_to_db(
        self, user_data: types.User, staff=True
    ):
        """Update user profile to database"""

        query = """
                INSERT OR REPLACE INTO telegram_bot_users
                (user_id, username, full_name, staff)
                VALUES (?,?,?,?)
            """
        params = (user_data.id, user_data.username, user_data.full_name, staff)

        with self._connect_sql:
            self._cursor.execute(query, params)
            self._connect_sql.commit()

    async def set_duty_user_to_db(
        self, user_id, staff: bool = False, duty: bool = False
    ):
        """Assign a user to the duty team"""

        query = "UPDATE telegram_bot_users SET "
        conditions = []
        params = []

        if staff:
            conditions.append("staff = ?")
            params.append(staff)
        if duty:
            conditions.append("duty = ?")
            params.append(duty)

        if not conditions:
            raise ValueError("At least one of 'staff' or 'duty' must be True")

        query += " , ".join(conditions) + " WHERE user_id = ?"
        params.append(user_id)

        with self._connect_sql:
            self._cursor.execute(query, params)
            self._connect_sql.commit()

    async def get_users_from_db(self, staff_only=False, duty_only=False):
        """Retrieve users' profile information from the database"""

        query = "SELECT * FROM telegram_bot_users"
        conditions = []

        if staff_only:
            conditions.append("staff = 1")
        if duty_only:
            conditions.append("duty = 1")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        with self._connect_sql as connection:
            # Fetch the results as a list of dictionaries
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            return cursor.execute(query).fetchall()

    async def delete_user_profile_from_db(self, user_id):
        """Delete a user from the database"""

        query = """DELETE FROM telegram_bot_users WHERE user_id=(?)"""
        with self._connect_sql:
            self._cursor.execute(query, (user_id,))
            self._connect_sql.commit()

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
        hosts = self._cursor.fetchall()
        self.logger.info("Host names retrieved from the database")

        return hosts

    async def delete_one_host_from_db(self, host: tuple[str]) -> None:
        """Delete a single host from the database"""

        with self._connect_sql:
            self._cursor.execute(
                "DELETE FROM failed_resources WHERE host_name = (?)", host
            )
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
                self.logger.info("Host added to the database: %s", host)
            else:
                await self.delete_one_host_from_db(host)
                self.logger.info("Host deleted from the database: %s", host)

        return result
