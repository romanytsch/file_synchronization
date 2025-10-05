import requests
import os
import logging

class Sync:
    """
        Класс для синхронизации файлов с Яндекс.Диском через REST API.

        Атрибуты:
            token (str): OAuth токен для авторизации в API.
            remote_folder (str): Путь к папке на Яндекс.Диске для синхронизации.
        """
    def __init__(self, token, remote_folder):
        """
            Инициализация экземпляра Sync.

            Args:
                token (str): OAuth токен для доступа к API.
                remote_folder (str): Путь к папке на диске (например, '/sync_folder').
            """
        self.token = token
        self.remote_folder = remote_folder.rstrip('/')
        self.headers = {"Authorization": f"OAuth {self.token}"}
        self.api_url = "https://cloud-api.yandex.net/v1/disk/resources"


    def load(self, local_path: str) -> None:
        """
            Загружает файл из локальной директории на Яндекс.Диск.

            Args:
                local_path (str): Полный путь к локальному файлу.

            Raises:
                requests.HTTPError: При ошибках HTTP-запросов.
            """
        filename = os.path.basename(local_path)
        remote_path = f"{self.remote_folder}/{filename}"

        # Получаем URL для загрузки
        params = {"path": remote_path, "overwrite": "true"}
        response = requests.get(f"{self.api_url}/upload", headers=self.headers, params=params)
        response.raise_for_status()
        upload_url = response.json().get("href")

        # Загружаем файл
        with open(local_path, "rb") as f:
            upload_response = requests.put(upload_url, data=f)
            upload_response.raise_for_status()

        logging.info(f"Файл {local_path} загружен в {remote_path}")


    def reload(self, local_path: str) -> None:
        """
            Перезаписывает файл на Яндекс.Диске, вызывая загрузку.

            Args:
                local_path (str): Полный путь к локальному файлу.
            """
        self.load(local_path)
        logging.info(f"Файл {os.path.basename(local_path)} перезаписан в удалённом хранилище")


    def delete(self, filename: str) -> bool:
        """
            Удаляет файл из удаленной папки на Яндекс.Диске.

            Args:
                filename (str): Имя файла для удаления.

            Returns:
                bool: True при успешном удалении, иначе False.
            """
        remote_path = f"{self.remote_folder}/{filename}"
        params = {"path": remote_path}
        response = requests.delete(self.api_url, headers=self.headers, params=params)
        if response.status_code == 204:
            logging.info(f"Файл {filename} успешно удалён из {self.remote_folder}")
            return True
        else:
            logging.info(f"Ошибка при удалении файла {filename}: {response.status_code} - {response.text}")
            return False

    def get_info(self):
        """
            Получает список файлов и папок внутри удалённой папки.

            Returns:
                List[Dict[str, Any]]: Список элементов с данными о файлах/папках.
            """
        params = {"path": self.remote_folder, "limit": 1000}
        response = requests.get(self.api_url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("_embedded", {}).get("items", [])