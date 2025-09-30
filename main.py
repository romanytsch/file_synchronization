import os

from storage_algorithm import Sync
from config import TOKEN, YANDEX_DISK_PATH, LOCAL_FOLDER


if __name__ == "__main__":
    sync = Sync(TOKEN, YANDEX_DISK_PATH)  # создаём объект класса
    files = sync.list_remote_files(YANDEX_DISK_PATH)  # вызываем метод через объект

    for filename in os.listdir(LOCAL_FOLDER):
        local_path = os.path.join(LOCAL_FOLDER, filename)
        remote_path = f"{YANDEX_DISK_PATH}/{filename}"
        sync.load(local_path, remote_path)

    print(files)