# Исключения
class SyncError(Exception):
    """Базовое исключение для всех ошибок синхронизации."""
    pass

# Ошибки, связанные с локальной директорией
class LocalError(SyncError):
    """Ошибки связанные с локальной директорией."""
    pass

class LocalFolderNotFoundError(LocalError):
    """Локальная папка не найдена."""
    def __init__(self, folder_path):
        super().__init__(f"Локальная папка не найдена: '{folder_path}'. Пожалуйста, проверьте путь.")



# Ошибки, связанные с удалённым API
class RemoteError(SyncError):
    """Ошибки связанные с удалённым API."""
    pass

class RemoteAccessError(RemoteError):
    """Ошибка доступа к API."""
    def __init__(self, details=""):
        msg = "Ошибка доступа к API Яндекс.Диска."
        if details:
            msg += f" Подробности: {details}"
        super().__init__(msg)

class RemoteResourceNotFoundError(RemoteError):
    """Ошибка 404 — ресурс не найден."""
    def __init__(self, path):
        msg = (f"Ресурс '{path}' не найден на Яндекс.Диске (Ошибка 404). "
               "Проверьте правильность пути и существование папки.")
        super().__init__(msg)



# Ошибки, связанные с файлами
class FileError(SyncError):
    """Ошибки связанные с файлами."""
    pass

class FileUploadError(FileError):
    """Ошибка загрузки файла."""
    def __init__(self, filename, details=""):
        msg = f"Ошибка загрузки файла '{filename}'."
        if details:
            msg += f" Подробности: {details}"
        super().__init__(msg)

class FileDeleteError(FileError):
    """Ошибка удаления файла из облака."""
    def __init__(self, filename, details=""):
        msg = f"Ошибка удаления файла '{filename}' из облака."
        if details:
            msg += f" Подробности: {details}"
        super().__init__(msg)
