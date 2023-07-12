Для сборки приложения используйте команду:

sudo docker build -t stand .

Для запуска:

sudo docker run -e HOST_IP="192.168.0.100" -p 8000:8000 stand

где значение HOST_IP нужно заменить на ip адрес устройства
