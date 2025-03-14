from src.parser.ArticleParser.BaseParser import BaseParser
import asyncio
import time

from src.ConfigManager.ConfigManager import ConfigManager
from src.logger import logger
from urllib.parse import urlparse


class GetArticleFast(BaseParser):
    def __init__(self):
        super().__init__()

    async def GetArticleRan(self, url, cookies):
        config = ConfigManager()
        proxies = await config.get_value("proxy")  # список проксі
        if not proxies:
            await logger.error("Proxy list is empty!")
            return None

        # Цикл по проксі
        for attempt in range(5):
            proxy = proxies[attempt % len(proxies)]  # бере проксі по черзі, повертається до першого після останнього
            proxy_url = self.construct_proxy_url(proxy)

            try:
                stat_time = time.time()
                response = await asyncio.to_thread(self.fetchData, url=url, timeout=5, proxy=proxy_url, cookies=cookies)
                await logger.info(f"Time: {time.time() - stat_time} seconds using proxy {proxy_url}")

                article_element = self.get_text_element_html(
                    html=response.text,
                    element='div',
                    class_='faq-anns-articleContent',
                    identifier='class',
                    return_soup=True
                )

                if not article_element:
                    await logger.warning(f"No article container found using proxy {proxy_url}")
                    continue  # Пробуємо з іншим проксі

                article_elements = self.get_text_elements_html(
                    html=article_element,
                    element='div',
                    class_=None,
                    identifier=None
                )

                if not article_elements:
                    await logger.warning(f"No article elements found using proxy {proxy_url}")
                    return None

                # Фільтруємо елементи
                filtered_elements = article_elements[:-1] if len(article_elements) > 1 else article_elements
                return ' '.join(element.text for element in filtered_elements)

            except Exception as e:
                await logger.error(f"Error with proxy {proxy_url}: {e}")
                continue  # Пробуємо наступний проксі

        # Якщо не вдалося дістати дані за 5 спроб, повертаємо None
        await logger.error("Failed to retrieve data after 5 attempts with different proxies")
        return None

    @staticmethod
    def construct_proxy_url(proxy):
        """Створює правильний URL для проксі"""
        parsed_proxy = urlparse(proxy)
        if parsed_proxy.username and parsed_proxy.password:
            return f"{parsed_proxy.scheme}://{parsed_proxy.username}:{parsed_proxy.password}@{parsed_proxy.hostname}:{parsed_proxy.port}"
        else:
            return proxy

if __name__ == '__main__':
     r = asyncio.run(GetArticleFast().GetArticleRan(url="https://www.binance.com/en/support/announcement/detail/5b3221ba1f494e57a005d8dd8695e135"))
     print(r)