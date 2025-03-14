import asyncio
import json
import os
import aiofiles
from src.logger import logger

class ConfigManager:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config_PATH = os.path.join(BASE_DIR, "config.json")
        self.file_path = config_PATH

    # Читання конфігурації з файлу
    async def read_config(self):
        if os.path.exists(self.file_path):
            try:
                async with aiofiles.open(self.file_path, "r") as file:
                    content = await file.read()
                    return json.loads(content)
            except (json.JSONDecodeError, IOError) as e:
                await logger.error(f"Помилка читання конфігурації: {str(e)}")
                return {}
        await logger.error("Файл конфігурації не знайдено")
        return {}

    # Оновлення значень у конфігурації
    async def update_value_in_file(self, key, value):
        data = await self.read_config()

        # Перевіряємо, чи ключ вже існує в конфігурації
        if key in data:
            data[key] = value

            # Перезаписуємо файл з оновленим значенням
            try:
                async with aiofiles.open(self.file_path, "w") as file:
                    await file.write(json.dumps(data, indent=4))
            except IOError as e:
                await logger.error(f"Помилка при збереженні конфігурації: {str(e)}")

    async def set_proxy_list(self, proxy_list):
        try:
            # Оновлення проксі у конфігурації
            await self.add_key_value("proxy", proxy_list)
            await logger.info(f"Proxy list set to: {proxy_list}")
            return True
        except Exception as e:
            await logger.error(f"Failed to set proxy list: {e}")
            return False

    # Додаємо новий ключ і значення в конфігурацію
    async def add_key_value(self, key, value):
        # Зчитуємо поточну конфігурацію
        data = await self.read_config()

        # Додаємо новий ключ і значення, якщо його немає
        data[key] = value  # Замість перевірки, одразу оновлюємо значення

        # Перезаписуємо файл з новим значенням
        try:
            async with aiofiles.open(self.file_path, "w") as file:
                await file.write(json.dumps(data, indent=4))
            await logger.info(f"Updated config: {data}")
        except IOError as e:
            await logger.error(f"Error saving data: {str(e)}")

    async def get_value(self, key):
        data = await self.read_config()
        return data.get(key, None)
