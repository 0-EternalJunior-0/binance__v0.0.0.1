import json
import re
import sys

from bs4 import BeautifulSoup
from lxml import html
from src.parser.ArticleParser.BaseParser import BaseParser
import asyncio
from src.logger import logger
from src.ConfigManager.ConfigManager import ConfigManager


class GetArticleDetailed(BaseParser):
    def __init__(self):
        super().__init__()

    def find_body(self, data, keyText='contentJson'):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'footer':
                    continue
                if key == keyText:
                    return value
                result = self.find_body(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_body(item)
                if result:
                    return result

    async def parserScript(self, script_tag):
        if script_tag:
            json_data = script_tag.string.strip()
            try:
                parsed_json = json.loads(json_data)

                body_data = self.find_body(parsed_json)

                if body_data:
                    return body_data
                else:
                    return None

            except json.JSONDecodeError as e:
                await logger.error(f"Помилка при розборі JSON: {e}")
                return None
        else:
            await logger.error("Елемент <script> з id='__APP_DATA' не знайдено.")
            return None

    async def extract_text(self, data):
        texts = []

        if isinstance(data, list):
            tasks = [self.extract_text(item) for item in data]
            results = await asyncio.gather(*tasks)
            for result in results:
                texts.extend(result)

        elif isinstance(data, dict):
            if 'config' in data and 'content' in data['config']:
                content = data['config']['content']
                if isinstance(content, str):
                    texts.append(content)
                elif isinstance(content, list):
                    texts.extend(await self.extract_text(content))

            if 'config' in data and 'data' in data['config'] and 'header' in data['config']:
                headers = data['config']['header']
                data_entries = data['config']['data']
                # Паралельно обробляємо всі елементи з data_entries
                tasks = []
                for entry in data_entries:
                    for header in headers:
                        if header in entry:
                            tasks.append(self.extract_text(entry[header]))
                # Очікуємо виконання всіх задач
                results = await asyncio.gather(*tasks)
                for result in results:
                    texts.extend(result)

        return texts

    @staticmethod
    async def textReplace(text):
        text = html.fromstring(text)
        text = text.text_content()  # Отримуємо тільки текст

        # Очищаємо текст від зайвих пробілів та специфічних символів
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\xa0', ' ')
        text = text.replace('вЂ¦', '...')
        text = text.replace('вЂњ', '"')
        text = text.replace('вЂќ', '"')
        text = text.replace('вЂ™', "'")

        # Додаткові символи, які можуть виникнути:
        text = text.replace('&#160;', ' ')
        text = text.replace('&#39;', "'")
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')

        return text

    async def run(self, url, script_tag='__APP_DATA', cookies=None):
        config = ConfigManager()
        proxy_list = await config.get_value("proxy") or [None]  # Додаємо None, якщо проксі немає
        Log_Details = await config.get_value("Log_Details")
        if proxy_list == None or proxy_list == [] or proxy_list == ['']:
            proxy_list = None
        else:
            proxy_list = proxy_list
        proxy_url = self.parse_proxy(proxy_list, Log_Details) if proxy_list else None

        if Log_Details:
            await logger.info(f"🔍 Використання проксі: {proxy_url if proxy_url else 'Без проксі'}")
        try:

            html_content = await asyncio.to_thread(self.fetchData, url=url, proxy=proxy_url, cookies=cookies)
            soup = BeautifulSoup(html_content.text, "html.parser")

            script_element = soup.find("script", {"id": script_tag})
            if not script_element:
                await logger.error("❌ Елемент <script> не знайдено. Перевірте HTML або URL.")

            body_data = await self.parserScript(script_element)
            if not body_data:
                await logger.error("❌ Неможливо розпарсити JSON з script-тегу.")

            body_data = json.loads(body_data)
            layout = body_data['layout']['ViewInstance0']

            content = []
            for i in layout:
                texts = await self.extract_text(body_data['hash'][i])
                content.extend(texts)

            text = ' '.join(content)
            return await self.textReplace(text)

        except Exception as e:
            await logger.error(str(e))

# if __name__ == '__main__':
#     url = 'https://www.binance.com/en/support/announcement/detail/5b3221ba1f494e57a005d8dd8695e135'
#     asyncio.run(GetArticleDetailed().run(url))
