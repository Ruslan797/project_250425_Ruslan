class LogStats:
    """
    Класс для анализа статистики логов поисковых запросов,
    сохранённых в MongoDB (через log_writer.collection).
    """
    def __init__(self, log_search):
        # Сохраняем коллекцию MongoDB из переданного log_writer
        self.collection = log_search.collection

    def get_popular(self, limit=5):
        """
        Получить топ популярных поисков на основе количества повторений.
        Группировка только по типу поиска.
        :param limit: по дефолту 5
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$search_type",  # Группировка только по типу поиска
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},  # Сортируем по убыванию
            {"$limit": limit},  # Ограничение количества результатов
            {
                "$project": {
                    "_id": 0,
                    "search_type": "$_id",  # Возвращаем тип поиска
                    "count": 1
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))

    def get_popular_genre(self, limit=5):
        """
        Получить топ популярных запросов по жанру и диапазону лет.
        :param limit: количество результатов
        """
        pipeline = [
            {"$match": {
                "search_type": "by genre and years",
                "parameters.genre": {"$exists": True},
                "parameters.from": {"$exists": True},
                "parameters.to": {"$exists": True}
            }},
            {"$group": {
                "_id": {
                    "genre": "$parameters.genre",
                    "from": "$parameters.from",
                    "to": "$parameters.to"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "genre": "$_id.genre",
                "from": "$_id.from",
                "to": "$_id.to",
                "count": 1
            }}
        ]
        return list(self.collection.aggregate(pipeline))

    def get_latest(self, limit=5):
        """
        Получить последние уникальные поисковые запросы, отсортированные по времени (timestamp).
        :param limit: по дефолту 5
        """
        pipeline = [
            {"$sort": {"timestamp": -1}},  # Сортировка по убыванию времени
            {
                "$group": {
                    "_id": {
                        "search_type": "$search_type",
                        "params": "$parameters"
                    },
                    "count": {"$first": "$result_count"},
                    "timestamp": {"$first": "$timestamp"},
                    "doc": {"$first": "$$ROOT"}
                }
            },
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "search_type": "$doc.search_type",
                    "params": {
                        "$reduce": {
                            "input": {
                                "$map": {
                                    "input": {"$objectToArray": "$doc.parameters"},
                                    "as": "p",
                                    "in": {"$toString": "$$p.v"}
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
                    "count": "$doc.result_count"
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))


    def get_popular_films_by_title(self, limit=5):
        """
        Получить топ популярных фильмов по названию.
        """
        pipeline = [
            {"$match": {"search_type": "by title"}},
            {"$addFields": {
                "normalized_title": {"$toLower": "$parameters.title"}
            }},
            {"$group": {
                "_id": "$normalized_title",
                "count": {"$sum": 1},
                "original_title": {"$first": "$parameters.title"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "title": "$original_title",
                "count": 1
            }}
        ]
        return list(self.collection.aggregate(pipeline))

    def get_popular_actors(self, limit=5):
        """Получить топ популярных актеров."""
        pipeline = [
            {"$match": {"search_type": "by actor"}},
            {"$group": {
                "_id": "$parameters.actor",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "actor_name": "$_id",
                "count": 1
            }}
        ]
        return list(self.collection.aggregate(pipeline))


