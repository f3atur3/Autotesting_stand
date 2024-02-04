# Сборка образа
## Для сборки приложения используйте команду:

`sudo docker build -t stand .`

## Для запуска:

`sudo docker run -p 8000:8000 stand`

# Запуск готового образа без сборки
## Для запуска приложения необходимо авторизироваться:

`sudo docker login ghcr.io`

где нужно ввести учетные данные GitHub (имя пользователя и персональный доступный токен), чтобы аутентифицироваться в GitHub Container Registry.

## Затем, чтобы скачать Docker-образ из GitHub Container Registry:

`sudo docker pull ghcr.io/f3atur3/autotesting_stand:latest`

## Для запуска:

`sudo docker run -p 8000:8000 ghcr.io/f3atur3/autotesting_stand:latest`
