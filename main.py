import os
import logging
import time
from storage_algorithm import Sync
from config import TOKEN, YANDEX_DISK_PATH, LOCAL_FOLDER, LOG_PATH, SYNC_PERIOD
from errors import SyncError

logging.basicConfig(
    filename=LOG_PATH if LOG_PATH else 'sync.log',
    level=logging.INFO,
    format='synchroniser %(asctime)s.%(msecs)03d %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def main():
    """
        Основная функция синхронизации: загружает новые или изменённые файлы,
        удаляет из облака файлы, которых нет локально.
        Логирует каждый шаг и ошибки.
        """

    logging.info("Начало синхронизации")

    if not os.path.exists(LOCAL_FOLDER) or not os.path.isdir(LOCAL_FOLDER):
        msg = f"Локальная директория не найдена: {LOCAL_FOLDER}"
        logging.error(msg)
        return None

    sync = Sync(TOKEN, YANDEX_DISK_PATH)

    try:
        items = sync.get_info()
        remote_files = {item['name']: item for item in items if 'name' in item}
        logging.info(f"Удалённые файлы: {list(remote_files.keys())}")
    except Exception as ex:
        msg = f"Ошибка доступа к Яндекс.Диску: {ex}"
        logging.error(msg)
        return None

    local_files = {file: os.path.getsize(os.path.join(LOCAL_FOLDER, file))
                   for file in os.listdir(LOCAL_FOLDER) if os.path.isfile(os.path.join(LOCAL_FOLDER, file))}
    logging.info(f"Локальные файлы: {list(local_files.keys())}")

    local_names = set(local_files.keys())
    remote_names = set(remote_files.keys())

    # Обработка загрузки (файлы, которых нет на удалённом или размер отличается)
    files_to_upload = {name for name in local_names if
                       (name not in remote_names) or (local_files[name] != remote_files[name]['size'])}
    for filename in files_to_upload:
        local_path = os.path.join(LOCAL_FOLDER, filename)
        try:
            sync.load(local_path)
            logging.info(f"Файл {filename} загружен или обновлён")
        except Exception as ex:
            logging.error(f"Ошибка загрузки файла {filename}: {ex}")

    # Обработка удаления (файлы, которые есть в удалённом, но отсутствуют локально)
    files_to_delete = remote_names - local_names
    for filename in files_to_delete:
        try:
            deleted = sync.delete(filename)
            if deleted:
                logging.info(f"Файл {filename} удалён из облака")
            else:
                logging.error(f"Не удалось удалить файл {filename} из облака")
        except Exception as ex:
            logging.error(f"Ошибка удаления файла {filename}: {ex}")

    logging.info("Синхронизация завершена")


if __name__ == "__main__":
    main()  # Первая синхронизация

    interval_seconds = int(SYNC_PERIOD)

    try:
        while True:
            time.sleep(interval_seconds)
            main()
    except KeyboardInterrupt:
        logging.info("Программа завершена пользователем")