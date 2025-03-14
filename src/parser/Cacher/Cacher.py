import json
import os
from typing import TextIO

from src.logger import logger


class Cacher:
    def __init__(self):
        self.SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'checkIdArticles.json')

    def load_checkIdArticles(self):
        """Завантажує ID статей з файлу. Якщо файл порожній або зіпсований — повертає пустий набір."""
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    if data:
                        return set(json.loads(data))
                    return set()
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Помилка декодування JSON: {e}")
                return set()
            except OSError as e:
                logger.error(f"Помилка доступу до файлу: {e}")
                return set()
        else:
            logger.error(f"Файл {self.SAVE_FILE} не знайдений.")
            return set()

    def save_checkIdArticles(self, checkIdArticles):
        """Зберігає ID статей у файл."""
        try:
            with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(list(checkIdArticles), f, ensure_ascii=False, indent=4)
        except OSError as e:
            logger.error(f"Помилка запису в файл: {e}")
