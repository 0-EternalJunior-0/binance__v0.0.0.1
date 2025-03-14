import requests

url = "https://example.com"
headers = {
    "cookie": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

# Отримання куків з відповіді
cookies = response.cookies

print(cookies)
