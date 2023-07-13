# Используем базовый образ Python
FROM python:3.10

# Устанавливаем переменные окружения для локали
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

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

# Устанавливаем пакет locales и генерируем локаль ru_RU.UTF-8
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=ru_RU.UTF-8

# Запускаем команду для миграций и сбора статических файлов
RUN python manage.py migrate

# Открываем порт, на котором будет работать Django при запуске контейнера
EXPOSE 8000

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]