from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()
#
# class LogSearch:
#     """
#     Класс для логирования поисковых запросов в MongoDB.
#     """
#
#     def __init__(self):
#         # Подключение к MongoDB
#         try:
#             self.client = MongoClient(os.getenv("MONGO_URI"))
#             self.db = self.client[os.getenv("MONGO_DB_NAME")]
#             self.collection = self.db[os.getenv("MONGO_COLLECTION_NAME")]
#         except Exception as e:
#             raise Exception(f"Failed to connect to MongoDB: {e}")
#         # self.client = MongoClient(os.getenv("MONGO_URI"))
#         # self.db = self.client[os.getenv("MONGO_DB_NAME")]
#         # self.collection = self.db[os.getenv("MONGO_COLLECTION_NAME")]
#
#     def log_search(self, search_type, parameters, result_count):
#         """
#         Логирует поисковый запрос.
#         :param search_type: тип поиска (по названию, жанру и т.д.)
#         :param parameters: параметры запроса (словарь)
#         :param result_count: количество найденных результатов
#         """
#         log_entry = {
#             "search_type": search_type,
#             "parameters": parameters,
#             "result_count": result_count,
#             "timestamp": datetime.now()
#         }
#         self.collection.insert_one(log_entry)


        # 2. var

class LogSearch:
    """Класс для логирования поисковых запросов в MongoDB."""

    def __init__(self):
        try:
            self.client = MongoClient(os.getenv("MONGO_URI"))
            self.db = self.client[os.getenv("MONGO_DB_NAME")]
            self.collection = self.db[os.getenv("MONGO_COLLECTION_NAME")]
        except Exception as e:
            raise Exception(f"Failed to connect to MongoDB: {e}")

    def _normalize_params(self, params):
        """Нормализует параметры: сортировка ключей, приведение строк к нижнему регистру, удаление пробелов."""
        normalized = {}
        for key in sorted(params.keys()):
            value = params[key]
            if isinstance(value, str):
                value = value.strip().lower()
            normalized[key] = value
        return normalized

    def log_search(self, search_type, parameters, result_count):
        """Логирует поисковый запрос."""
        normalized_params = self._normalize_params(parameters)
        log_entry = {
            "search_type": search_type.strip().lower(),
            "parameters": normalized_params,
            "result_count": result_count,
            "timestamp": datetime.now()
        }

        try:
            self.collection.insert_one(log_entry)
        except Exception as e:
            print(f"Failed to log search: {e}")

