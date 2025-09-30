import requests
import os

class Sync:
    def __init__(self, token, remote_path):
        self.token = token
        self.remote_path = remote_path
        self.headers = {"Authorization": f"OAuth {self.token}"}
        self.api_url = "https://cloud-api.yandex.net/v1/disk/resources"

    def list_remote_files(self, path):
        params = {"path": path}
        response = requests.get(self.api_url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("items", [])

    def load(self, local_path, remote_path):
        params = {"path": remote_path, "overwrite": "true"}
        response = requests.get(f"{self.api_url}/upload", headers=self.headers, params=params)
        response.raise_for_status()
        upload_url = response.json()["href"]

        with open(local_path, "rb") as f:
            upload_response = requests.put(upload_url, data=f)
            upload_response.raise_for_status()
        print(f"Файл {local_path} загружен в {remote_path}")


    def reload(self, local_folder, remote_folder):
        # Получаем список файлов и папок из remote_folder
        remote_files = {item["name"]: item for item in self.list_remote_files(remote_folder)}

        # Перебираем локальные файлы для синхронизации
        for filename in os.listdir(local_folder):
            local_path = os.path.join(local_folder, filename)
            remote_path = f"{remote_folder}/{filename}"

            # Если файла нет в облаке либо размер отличается — перезаписываем
            if (filename not in remote_files
                    or os.path.getsize(local_path) != remote_files[filename]["size"]):
                self.load(local_path, remote_path)
                print(f"Файл {filename} перезаписан на Яндекс.Диске")


    def delete(self, filename):
        params = {"path": filename}
        response = requests.delete(self.api_url, headers=self.headers, params=params)
        if response.status_code == 204:
            print(f"Файл {filename} успешно удалён")
            return True
        else:
            print(f"Ошибка при удалении файла {filename}: {response.status_code} - {response.text}")
            return False

    def get_info(self):
        params = {"path": self.remote_path}
        response = requests.get(self.api_url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
