class LogStats:
    """
    Класс для анализа статистики логов поисковых запросов,
    сохранённых в MongoDB (через log_writer.collection).
    """
    def __init__(self, log_writer):
        # Сохраняем коллекцию MongoDB из переданного log_writer
        self.collection=log_writer.collection

    def get_popular(self, limit=5):
        """
        Получить топ популярных поисков на основе количества повторений.
        Группировка по типу поиска и параметрам.
        :param limit: по дефолту 5
        """
        row=[
            {
                "$group": {
                    "_id": {
                        "type": "$search_type", # Группировка по типу запроса и по переданным параметрам
                        "params": "$params"
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},   # Сортируем по убыванию
            {"$limit": limit},   # Ограничение количества результатов
            {
                "$project": {
                    "_id": 0,
                    "search_type": "$_id.type",  # Возвращаем тип поиска
                    "params": {
                        # Преобразуем словарь параметров в строку через запятую
                        "$reduce": {
                            "input": {
                                "$map": {
                                    "input": {"$objectToArray": "$_id.params"},
                                    "as": "p",
                                    "in": {"$toString": "$$p.v"}  # Только значения, не ключи
                                }
                            },
                            "initialValue": "",
                            "in": {
                                "$cond": [
                                    {"$eq": ["$$value", ""]},
                                    "$$this",
                                    {"$concat": ["$$value", ", ", "$$this"]}
                                ]
                            }
                        }
                    },
                    "count": 1
                }
            }
        ]
        return list(self.collection.aggregate(row))


    def get_latest(self,limit=5):
        """
        Получить последние поисковые запросы, отсортированные по времени (timestamp).
        :param limit: по дефолту 5
        """
        row=[
            {"$sort": {"timestamp": -1}},   # Сортировка по убыванию времени Ограничиваем количество
                    {"$limit": limit},
                    {
                        "$project": {
                            "_id": 0,
                            "search_type": 1,
                            "params": {
                                # Преобразуем параметры в строку
                                "$reduce": {
                                    "input": {
                                        "$map": {
                                            "input": {"$objectToArray": "$params"},
                                            "as": "p",
                                            "in": {"$toString": "$$p.v"}  # Только значения
                                        }
                                    },
                                    "initialValue": "",
                                    "in": {
                                        "$cond": [
                                            {"$eq": ["$$value", ""]},
                                            "$$this",
                                            {"$concat": ["$$value", ", ", "$$this"]}
                                        ]
                                    }
                                }
                            },
                            "count": "$results_count" # Показываем, сколько результатов дал поиск
                        }
                    }
        ]
        return list(self.collection.aggregate(row))