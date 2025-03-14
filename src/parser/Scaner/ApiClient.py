import asyncio
import aiohttp
from fake_useragent import UserAgent
from src.logger import logger

class ApiClient:
    """Клас для виконання запитів до API."""
    def __init__(self, api_url, params=None):
        self.api_url = api_url
        self.params = params or {}

    async def fetch_data(self, session):
        """Виконує асинхронний запит до API."""
        headers = {"User-Agent": UserAgent().random}
        try:
            async with session.get(self.api_url, params=self.params, headers=headers, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return (data.get("data") or {}).get("catalogs", [])
                else:
                    await logger.error(f"Помилка при скануванні {response.status}")
        except asyncio.TimeoutError:
            await logger.error("❌ Час запиту вийшов")
        except aiohttp.ClientError as e:
            await logger.error(f"❌ Помилка клієнта: {e}")
        except Exception as e:
            await logger.error(f"❌ Невідома помилка: {e}")
        return []
