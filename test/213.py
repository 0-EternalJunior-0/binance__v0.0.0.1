from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests

def get_cookies(url):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(5)  # Дайте час для завантаження сторінки та виконання JS
    cookies = driver.get_cookies()  # Отримання куків
    driver.quit()  # Закриваємо браузер
    return cookies

# Ваш URL
url = "https://www.binance.com/en/support/announcement/detail/4b88b1f8848444d9ad7af3d406bff72e"

# Отримуємо куки
cookies = get_cookies(url=url)

# Перетворюємо куки у формат, який розуміє requests
cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
print(cookies_dict)

# Заголовки для запиту
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

# Виконання запиту з куками
response = requests.get(url, headers=headers, cookies=cookies_dict)

# Перевіряємо результат
print(response.status_code)
print(response.text)  # або response.content для бінарних даних
