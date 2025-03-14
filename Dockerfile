# Використовуємо офіційний образ Selenium з Chrome
FROM selenium/standalone-chrome:latest

# Перемикаємося на користувача root, щоб мати доступ до системних пакетів
USER root

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл requirements.txt в контейнер
COPY requirements.txt .

# Оновлюємо пакети в системі та встановлюємо python3-venv для створення віртуального середовища
RUN apt-get update && apt-get install -y python3-venv

# Створюємо віртуальне середовище
RUN python3 -m venv /opt/venv

# Встановлюємо залежності з requirements.txt у віртуальному середовищі
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту в контейнер
COPY . .

# Використовуємо віртуальне середовище для запуску програми
CMD ["/opt/venv/bin/python", "main.py"]
