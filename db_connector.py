import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env
load_dotenv()

class DBConnector:
    """
    Класс для подключения и взаимодействия с базой данных MySQL.
    Все методы возвращают результат SQL-запросов.
    """

    def __init__(self):
        # Подключение к базе данных с использованием переменных окружения
        self.connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            cursorclass=DictCursor,
        )

    def search_by_title(self, name, offset=0, limit=10):
        """Поиск фильмов по названию."""
        query = """
            SELECT title
            FROM film
            WHERE LOWER(title) LIKE %s
            LIMIT %s OFFSET %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (f"%{name.lower()}%", limit, offset))
            return cursor.fetchall()

    def get_all_genres(self):
        """Получить список всех уникальных жанров."""
        query = "SELECT DISTINCT name FROM category"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return [row["name"] for row in cursor.fetchall()]


    def search_by_genre(self, genre):
        query = """
            SELECT f.title, f.release_year
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE LOWER(c.name) LIKE %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (f"%{genre.lower()}%",))
            return cursor.fetchall()


    def search_by_year_range(self, year_from=1990, year_to=2025):
        """Поиск фильмов в заданном диапазоне лет."""
        query = """
            SELECT title, release_year
            FROM film
            WHERE release_year BETWEEN %s AND %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (year_from, year_to))
            return cursor.fetchall()

    def search_by_genre_and_years(self, genre, year_from, year_to):
        """Поиск фильмов по жанру и диапазону лет."""
        query = """
            SELECT f.title, f.release_year, c.name AS genre
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name LIKE %s AND f.release_year BETWEEN %s AND %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (f"%{genre}%", year_from, year_to))
            return cursor.fetchall()

    def search_by_actor(self, actor_name):
        """Поиск фильмов по имени актёра."""
        query = """
            SELECT f.title, f.release_year, CONCAT(a.first_name, ' ', a.last_name) AS actor_name
            FROM film f
            JOIN film_actor fa ON f.film_id = fa.film_id
            JOIN actor a ON fa.actor_id = a.actor_id
            WHERE LOWER(CONCAT(a.first_name, ' ', a.last_name)) LIKE %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (f"%{actor_name.lower()}%",))
            return cursor.fetchall()



    def close(self):
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()
