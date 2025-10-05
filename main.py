import os
import logging
import time
import requests
from storage_algorithm import Sync
from config import TOKEN, YANDEX_DISK_PATH, LOCAL_FOLDER, LOG_PATH, SYNC_PERIOD
from errors import (
    SyncError, LocalFolderNotFoundError, RemoteAccessError,
    RemoteResourceNotFoundError, FileUploadError, FileDeleteError
)

logging.basicConfig(
    filename=LOG_PATH if LOG_PATH else 'sync.log',
    level=logging.INFO,
    format='synchroniser %(asctime)s.%(msecs)03d %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def main():
    logging.info(f"Программа запущена, синхронизируемая папка: {LOCAL_FOLDER}")

    # Проверка локальной папки
    if not os.path.exists(LOCAL_FOLDER) or not os.path.isdir(LOCAL_FOLDER):
        err = LocalFolderNotFoundError(LOCAL_FOLDER)
        logging.error(err)
        print(err)
        return None

    # Инициализация Sync с API
    try:
        sync = Sync(TOKEN, YANDEX_DISK_PATH)
    except Exception as e:
        err = RemoteAccessError(str(e))
        logging.error(err)
        print(err)
        return None

    # Получение списка файлов из облака
    try:
        items = sync.get_info()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            err = RemoteResourceNotFoundError(YANDEX_DISK_PATH)
            logging.error(err)
            print(err)
            return None
        else:
            err = RemoteAccessError(str(e))
            logging.error(err)
            print(err)
            return None
    except Exception as e:
        err = RemoteAccessError(str(e))
        logging.error(err)
        print(err)
        return None
    else:
        remote_files = {item['name']: item for item in items if 'name' in item}
        logging.info(f"Удалённые файлы: {list(remote_files.keys())}")


    # Получение локальных файлов и размеров
    try:
        local_files = {file: os.path.getsize(os.path.join(LOCAL_FOLDER, file))
                       for file in os.listdir(LOCAL_FOLDER)
                       if os.path.isfile(os.path.join(LOCAL_FOLDER, file))}
        logging.info(f"Локальные файлы: {list(local_files.keys())}")
    except Exception as e:
        err_msg = f"Ошибка доступа к локальной папке или файлам: {e}"
        logging.error(err_msg)
        print(err_msg)
        local_files = {}

    # Определение файлов для загрузки и удаления
    local_names = set(local_files.keys())
    remote_names = set(remote_files.keys())

    files_to_upload = {name for name in local_names
                       if (name not in remote_names) or (local_files[name] != remote_files[name]['size'])}


    # Загрузка новых и обновлённых файлов в облако
    for filename in files_to_upload:
        local_path = os.path.join(LOCAL_FOLDER, filename)
        try:
            sync.load(local_path)
            logging.info(f"Файл {filename} загружен или обновлён")
        except Exception as e:
            err = FileUploadError(filename, str(e))
            logging.error(err)
            print(err)


    # Удаление файлов из облака, отсутствующих локально
    files_to_delete = remote_names - local_names

    for filename in files_to_delete:
        try:
            deleted = sync.delete(filename)
            if deleted:
                logging.info(f"Файл {filename} удалён из облака")
            else:
                err = FileDeleteError(filename, "Не удалось удалить файл из облака")
                logging.error(err)
                print(err)
        except Exception as e:
            err = FileDeleteError(filename, str(e))
            logging.error(err)
            print(err)

    logging.info("Синхронизация завершена")


if __name__ == "__main__":
    try:
        while True:
            main()
            interval_seconds = int(SYNC_PERIOD)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
        logging.info(f"Программа остановлена пользователем")