import os
from dotenv import find_dotenv, load_dotenv

# Загружаем переменные окружения из файла .env
if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()


TOKEN = os.getenv("TOKEN")
YANDEX_DISK_PATH = os.getenv("YANDEX_DISK_PATH")
LOCAL_FOLDER = os.getenv("LOCAL_FOLDER")
