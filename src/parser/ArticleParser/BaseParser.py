import asyncio
import random
from urllib.parse import urlparse

import cloudscraper
from bs4 import BeautifulSoup, Tag
from cloudscraper.exceptions import CloudflareChallengeError
from requests.exceptions import RequestException
from fake_useragent import UserAgent
import backoff
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.logger import logger

class BaseParser:
    def __init__(self):
        self.ua = UserAgent()
        self.session = cloudscraper.create_scraper()
        self.user_agent = self.ua.random
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "x-requested-with": "XMLHttpRequest",
            "content-encoding": "gzip",
        })
        adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5))
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def update_headers(self, add_headers=None, new_headers=None):
        if add_headers:
            self.session.headers.update(add_headers)
        if new_headers:
            self.session.headers = new_headers

    @backoff.on_exception(backoff.expo, (CloudflareChallengeError, RequestException), max_tries=3)
    def __make_request(self, method, url, params=None, json_data=None, data=None, timeout=10, headers=None, proxy=None, cookies=None):
        """Приватний метод для обробки запитів GET та POST з однаковою логікою повтору та обробки помилок"""
        # Перевіряємо чи передано проксі
        proxies = None
        if proxy:
            # Якщо проксі передано, створюємо словник проксі для http та https
            proxies = {"http": proxy, "https": proxy}
        response = method(url, params=params, json=json_data, data=data, timeout=timeout, headers=headers, proxies=proxies, cookies=cookies)
        response.raise_for_status()
        return response

    def fetchData(self, url=None, params=None, json_data=None, data=None, timeout=10, headers=None, proxy=None, cookies=None):
        """Логіка для отримання даних (GET запит)"""
        return self.__make_request(self.session.get, url, params=params, json_data=json_data, data=data, timeout=timeout, headers=headers, proxy=proxy, cookies=cookies)

    def postData(self, url=None, params=None, json_data=None, data=None, timeout=10, headers=None, proxy=None):
        """Логіка для відправлення даних (POST запит)"""
        return self.__make_request(self.session.post, url, params=params, json_data=json_data, data=data, timeout=timeout, headers=headers, proxy=proxy)
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

    @staticmethod
    def get_text_element_html(html: str, element: str or None = None, class_: str or None = None, identifier='class', return_soup=False):
        """Отримання тексту з HTML"""
        try:
            soup = html if isinstance(html, Tag) else BeautifulSoup(html, 'lxml')
            if identifier == 'class':
                content_div = soup.find(element, class_=class_)
            elif identifier == 'id':
                content_div = soup.find(element, id=class_)
            else:
                content_div = soup.find(element)
            return content_div if return_soup else (content_div.get_text(strip=True) if content_div else None)
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def get_text_elements_html(html: str, element: str or None = None, class_: str or None = None, identifier='class'):
        try:
            soup = html if isinstance(html, Tag) else BeautifulSoup(html, 'lxml')
            if identifier == 'class':
                return soup.find_all(element, class_=class_)
            elif identifier == 'id':
                return soup.find_all(element, id=class_)
            else:
                return soup.find_all(element)
        except CloudflareChallengeError as e:
            logger.error(e)
            return None
