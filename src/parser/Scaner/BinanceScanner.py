import asyncio
import aiohttp
import time

import requests

from src.logger import logger
from src.parser.Scaner.ArticleProcessor import ArticleProcessor
from src.parser.Scaner.Scanner import Scanner
from urllib.parse import urlparse
import random


class BinanceScanner(Scanner):
    """Спеціалізований клас для сканування Binance."""
    def __init__(self, api_url, params=None):
        super().__init__(api_url, params)

    async def scanner_loop(self):
        """Основний цикл сканування."""
        asyncio.create_task(self.log_scanning_progress())
        while True:
            interval = await self.config.get_value("scan_interval")
            proxy = await self.config.get_value("proxy")
            Log_Details = await self.config.get_value("Log_Details")
            start_time = time.perf_counter()

            async with aiohttp.ClientSession() as session:
                try:
                    results = await self.api_client.fetch_data(session)
                    new_articles = await ArticleProcessor.filter_new_articles(results)
                    for article in new_articles:
                        yield article
                except Exception as e:
                    await logger.error(f"❌ Помилка при скануванні: {str(e)}")
            await self.wait_for_next_cycle(start_time, interval)

    async def log_scanning_progress(self):
        while True:
            await logger.info("⏳ Сканування триває...")
            await asyncio.sleep(60*10)  # Затримка на 10 хв

    @staticmethod
    def parse_proxy(proxy, Log_Details):
        """Форматує проксі URL для використання."""
        if not proxy or proxy == "" or proxy == []:
            return None
        if isinstance(proxy, list):
            proxy = random.choice(proxy)
        try:
            parsed_proxy = urlparse(proxy)
            proxy_url = (f"{parsed_proxy.scheme}://{parsed_proxy.username}:{parsed_proxy.password}@"
                         f"{parsed_proxy.hostname}:{parsed_proxy.port}" if parsed_proxy.username and parsed_proxy.password
                         else proxy)
            if Log_Details == 1:
                asyncio.create_task(logger.info(f"🛠 Використовується проксі: {proxy_url}"))
            return proxy_url
        except Exception as e:
            asyncio.create_task(logger.error(f"❌ Помилка при форматуванні проксі: {str(e)}"))
            return None


async def main():
    params = {
        "type": 1,
        "pageNo": 1,
        "pageSize": 2,
    }
    api_url = "https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query"
    scanner = BinanceScanner(api_url, params)
    async for article in scanner.scanner_loop():  # використовуйте async for для обробки асинхронного генератора
        print(article)  # обробка статей, що повертаються

if __name__ == "__main__":
    asyncio.run(main())  # запускаємо основну корутину