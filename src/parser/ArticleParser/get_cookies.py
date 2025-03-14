import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Функція для отримання куків
# Функція для отримання куків
async def get_cookies(url):
    loop = asyncio.get_event_loop()
    options = Options()
    options.add_argument("--headless")  # Запуск без графічного інтерфейсу
    options.add_argument("--no-sandbox")  # Для роботи в контейнері
    options.add_argument("--disable-dev-shm-usage")  # Для обмежених ресурсів

    # Підключення до Selenium через Docker
    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",  # Адреса контейнера Selenium
        options=options
    )

    driver.get(url)
    time.sleep(5)  # Чекати 5 секунд для завантаження сторінки

    cookies = driver.get_cookies()  # Отримання куків
    driver.quit()  # Закриваємо браузер
    return cookies


