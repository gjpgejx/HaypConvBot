# Используем официальный Python-образ
FROM python:3

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt в контейнер
COPY requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем содержимое текущей директории в контейнер
COPY . .

RUN mkdir temp

# Запускаем скрипт
CMD ["python", "main.py"]
