import asyncio
import time
from src.ConfigManager.ConfigManager import ConfigManager
from src.parser.Scaner.ApiClient import ApiClient

class Scanner:
    """Основний клас для сканування."""
    def __init__(self, api_url, params=None):
        self.api_client = ApiClient(api_url, params)
        self.config = ConfigManager()

    async def wait_for_next_cycle(self, start_time, interval):
        """Коригує час очікування до наступного циклу."""
        elapsed_time = time.perf_counter() - start_time
        sleep_time = max(interval - elapsed_time, 0)
        await asyncio.sleep(sleep_time)
