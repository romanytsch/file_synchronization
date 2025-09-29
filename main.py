import requests

from config import TOKEN

headers = {"Authorization": f"OAuth {TOKEN}"}

def get_disk_info():
    url = "https://cloud-api.yandex.net/v1/disk"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def list_root_files():
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": "/"}  # корневая папка

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def main():
    # Информация о диске
    disk_info = get_disk_info()
    print("Информация о диске:")
    print(disk_info)

    # Содержимое корня
    root_contents = list_root_files()
    print("\nСодержимое корневой директории:")
    for item in root_contents.get('items', []):
        print(f"{item['name']} - {item['type']}")

if __name__ == "__main__":
    main()