import asyncio
import dataclasses

import time

from src.Config import Config
from src.logger import logger
from src.parser.ArticleParser.GetArticleDetailed import GetArticleDetailed
from src.parser.ArticleParser.GetArticleFast import GetArticleFast
from src.parser.Scaner.BinanceScanner import BinanceScanner
from src.parser.Filter.Filter import Filter
from src.models.MessageQueueData import Data
from src.Server.send_message import send_message
from src.Server.WebSocket import ParserClient, websocket_listener
from src.parser.ArticleParser.get_cookies import get_cookies
from src.utility.time import format_timestamp_ms


cookies = None

# Функція для оновлення куків кожні 2 години
async def update_cookies_periodically(url, cookies_updated_event, interval=7200):
    global cookies
    while True:
        _cookies = await get_cookies(url)
        cookies = {cookie['name']: cookie['value'] for cookie in _cookies}
        await logger.info(f"Оновлені куки: {str(cookies)[:50]}")
        cookies_updated_event.set()  # Сигналізуємо, що куки оновлено
        await asyncio.sleep(interval)  # Чекати задану кількість секунд (2 години за замовчуванням)

async def main():
    # Створюємо подію для оновлення куків
    cookies_updated_event = asyncio.Event()

    # Запускаємо асинхронне оновлення куків в фоновому режимі
    asyncio.create_task(update_cookies_periodically(
        'https://www.binance.com/en/support/announcement/detail/5b3221ba1f494e57a005d8dd8695e135',
        cookies_updated_event
    ))
    await cookies_updated_event.wait()

    params = {
        "type": 1,
        "pageNo": 1,
        "pageSize": 2,
    }
    api_url = "https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query"

    scanner = BinanceScanner(api_url, params)
    parserFast = GetArticleFast()
    parserArticleDetailed = GetArticleDetailed()


    parser_client = ParserClient(Config.WS_URL)
    asyncio.create_task(websocket_listener(parser_client))
    async for article in scanner.scanner_loop():
        if article is None:
            continue
        try:
            filter = Filter()

            article = await filter.filter_cacher(article)
            if article is None:
                continue
            release_date = await format_timestamp_ms(article["releaseDate"] or 0)
            time_parsing = await format_timestamp_ms(int(time.time() * 1000))
            url = 'https://www.binance.com/en/support/announcement/' + article["code"]

            data = Data(
                title=article["title"],
                url=url,
                exchange='binance',
                releaseDate=release_date,
                timeParsing=time_parsing,
                catalogName=article["catalogName"]
            )

            text = await parserArticleDetailed.run(url=url, script_tag='__APP_DATA', cookies=cookies)
            if not text:
                text = await parserFast.GetArticleRan(url=url, cookies=cookies)
                if not text:
                    await logger.error('Резервна версія Парсера не змогла витягнути текст')
                    continue
                else:
                    await logger.error('Резервна версія Парсера завершена без помилок')
            data.text = text
            await send_message(
                message=dataclasses.asdict(data),
                url=Config.URL_MessageQueue,
                log = "📤 Відправляємо повідомлення на Сервер Message Queue"
            )

        except Exception as e:
            await logger.error(f"❌ Помилка при скануванні: {str(e)}")

# Запускаємо асинхронну функцію
if __name__ == "__main__":
    asyncio.run(main())
