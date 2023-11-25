import json
import aiohttp

from loader import env


class ApiUsersideData:
    """Class to interact with the userside API and fetch data."""

    def __init__(self):
        self.base_url = env.str("URL_USERSIDE")
        self.api_key = env.str("API_KEY_USERSIDE")
        self.url = f"{self.base_url}api.php?key={self.api_key}"

    async def fetch_data(self, params: dict) -> dict:
        """
        Fetch data from the API using aiohttp.

        Args:
            params (dict): Parameters to send with the API request.

        Returns:
            dict: The parsed JSON response from the API.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as response:
                text = await response.text()
                return json.loads(text)

    async def get_task(self, task_id: str) -> dict:
        """
        Get task data by task ID.

        Args:
            task_id (int): ID of the task.

        Returns:
            dict: Task data retrieved from the API.
        """
        params = {"cat": "task", "action": "show", "id": task_id}
        task_data = await self.fetch_data(params)
        return task_data

    async def get_customer(self, customer_id: str) -> dict:
        """
        Get customer data by customer ID.

        Args:
            customer_id (int): ID of the customer.

        Returns:
            dict: Customer data retrieved from the API.
        """
        params = {
            "cat": "customer",
            "subcat": "get_data",
            "customer_id": customer_id,
        }
        customer_data = await self.fetch_data(params)
        return customer_data
