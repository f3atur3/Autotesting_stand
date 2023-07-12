# Используем базовый образ Python
FROM python:3.10

# Устанавливаем переменную окружения для отключения вывода байт-кода Python
ENV PYTHONDONTWRITEBYTECODE 1

# Устанавливаем переменную окружения для отключения буферизации вывода
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app/

# Создаем виртуальную среду
RUN python -m venv venv

# Активируем виртуальную среду
RUN /bin/bash -c "source venv/bin/activate"

# Копируем файлы зависимостей в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем команду для миграций и сбора статических файлов
RUN python manage.py migrate

# Открываем порт, на котором будет работать Django при запуске контейнера
EXPOSE 8000

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]