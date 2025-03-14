import aiohttp


async def send_message(message, url: str=None, log: str=None):
    from src.logger import logger
    if log:
        await logger.info(log)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=message, timeout=2) as response:
                status = response.status
                try:
                    response_text = await response.text()
                except Exception as e:
                    response_text = f"Не вдалося отримати текст відповіді: {e}"

                if 200 <= status < 300:
                    await logger.info(f"✅ Успішно надіслано! Статус: {status}, Відповідь: {response_text}")
                else:
                    await logger.warning(f"⚠️ Помилка при надсиланні! Статус: {status}, Відповідь: {response_text}")

    except aiohttp.ClientError as e:
        await logger.error(f"❌ Помилка при відправці: {e}")
    except Exception as e:
        await logger.error(f"❌ Загальна помилка при відправці: {str(e)}")