from pymongo.errors import PyMongoError
from pymysql.err import MySQLError, OperationalError, ProgrammingError, InternalError
from db_connector import DBConnector
from log_writer import LogSearch
from formatter import GREEN, MAGENTA, RESET, BERUSA, RED
from log_stats import LogStats

def main_menu():
    print(f"{MAGENTA}\n*** WELCOME TO FILM SEARCH ***{RESET}")
    print("Choose search type:")
    print("1. Search by title")
    print("2. Search by genre and years")
    print("3. Search for popular queries")
    print("4. Search by actor")
    print("5. Exit")

    while True:
        choice_input = input(f"{GREEN}Your choice: {RESET}").strip()
        if not choice_input.isdigit():
            print("Please enter a number between 1 and 5.")
            continue
        choice = int(choice_input)
        if choice in range(1, 6):
            return choice
        else:
            print("Please choose a number between 1 and 5.")

def print_paginated_results(results, description_func=None, limit=10):
    offset = 0
    while True:
        batch = results[offset:offset + limit]
        if not batch:
            break
        for i, entry in enumerate(batch, offset + 1):
            if description_func:
                description = description_func(entry)
                print(f"{i}. {description}")
            else:
                print(f"{i}. {entry}")
        if len(batch) < limit:
            break
        user_input = input(f"\nПоказать ещё {limit} результатов? (y/n): ").strip().lower()
        if user_input != 'y':
            break
        offset += limit

def get_search_description(search_type):
    descriptions = {
        "by title": "По названию фильма",
        "by actor": "По актёру",
        "by genre and years": "По жанру и годам",
        "by years (from... to...)": "По диапазону лет",
        "by genre": "По жанру"
    }
    return descriptions.get(search_type, search_type)

def main():
    db = DBConnector()
    logger = LogSearch()
    stats = LogStats(logger)

    while True:
        choice = main_menu()
        if choice == 1:
            try:
                title = input("Enter film title: ")
                all_results = db.search_by_title(title, limit=1000)
            except Exception as e:
                print(f"{RED}Ошибка при поиске по названию: {e}{RESET}")
                continue

            def description_func(entry):
                return entry['title']
            print_paginated_results(all_results, description_func, limit=10)
            logger.log_search("by title", {"title": title}, len(all_results))

        elif choice == 2:
            try:
                genres = db.get_all_genres()
            except Exception as e:
                print(f"{RED}Ошибка при получении списка жанров: {e}{RESET}")
                continue
            print("Available genres:")
            for i, genre in enumerate(genres, 1):
                print(f"{i}. {genre}")
            genre_input = input("Choose genre (number or name): ").strip()
            if genre_input.isdigit():
                index = int(genre_input) - 1
                if index not in range(len(genres)):
                    print(f"{BERUSA}Invalid selection.{RESET}")
                    continue
                genre = genres[index]
            else:
                genre_matches = [g for g in genres if g.lower() == genre_input.lower()]
                if not genre_matches:
                    print(f"{BERUSA}Genre not found.{RESET}")
                    continue
                genre = genre_matches[0]
            try:
                print("Films ranging from 1990 to 2025: ")
                year_from = int(input("Year from: "))
                year_to = int(input("Year to: "))
                if year_from > year_to:
                    print(f'{RED}The starting year "{year_from}" cannot be later than the ending year "{year_to}".{RESET}')
                    continue
                if year_from < 1990 or year_to > 2025:
                    print(f'{RED}Please enter years from 1990 to 2025.{RESET}')
                    continue
                all_results = db.search_by_genre_and_years(genre, year_from, year_to, limit=1000)
                def description_func(entry):
                    return f"{entry['title']} ({entry['release_year']}) - {entry['genre']}"
                print_paginated_results(all_results, description_func, limit=10)
                logger.log_search("by genre and years", {"genre": genre, "from": year_from, "to": year_to}, len(all_results))
            except ValueError:
                print(f"{BERUSA}Invalid year input.{RESET}")


        elif choice == 3:
            print(f"\n{MAGENTA}Top 5 popular searches by genre and years:{RESET}")
            print(f"{'#':<3} {'Genre':<15} | {'Years':<15} | {'Requests':<10}")
            print('-' * 45)
            popular_genre_years = []
            try:
                popular_genre_years = stats.get_popular_genre(limit=5)
            except PyMongoError as e:
                print(f"{RED}Ошибка MongoDB: {e}{RESET}")
            except Exception as e:
                print(f"{RED}Непредвиденная ошибка: {e}{RESET}")

            for i, entry in enumerate(popular_genre_years, 1):
                genre = entry['genre'].capitalize()
                year_range = f"{entry['from']}–{entry['to']}"
                count = entry['count']
                print(f"{i:<3} {genre:<15} | {year_range:<15} | {count:<10}")

            print(f"\n{MAGENTA}Top 5 popular films by title:{RESET}")
            print(f"{'#':<3} {'Film Title':<30} | {'Requests':<10}")
            print('-' * 50)
            popular_films_by_title = []
            try:
                popular_films_by_title = stats.get_popular_films_by_title(limit=5)
            except PyMongoError as e:
                print(f"{RED}Ошибка MongoDB: {e}{RESET}")
            except Exception as e:
                print(f"{RED}Непредвиденная ошибка: {e}{RESET}")

            for i, entry in enumerate(popular_films_by_title, 1):
                film_title = entry.get('title', 'Unknown').upper()
                count = entry['count']
                print(f"{i:<3} {film_title:<30} | {count:<10}")
            print(f"\n{MAGENTA}Top 5 popular actors:{RESET}")
            print(f"{'#':<3} {'Actor':<25} | {'Requests':<10}")
            print('-' * 45)
            popular_actors = []
            try:
                popular_actors = stats.get_popular_actors(limit=5)
            except PyMongoError as e:
                print(f"{RED}Ошибка MongoDB: {e}{RESET}")
            except Exception as e:
                print(f"{RED}Непредвиденная ошибка: {e}{RESET}")

            for i, entry in enumerate(popular_actors, 1):
                actor_name = entry.get('actor_name', 'Unknown').capitalize()
                count = entry['count']
                print(f"{i:<3} {actor_name:<25} | {count:<10}")

            # Последние 5 запросов
            print(f"\n{MAGENTA}Latest 5 searches:{RESET}")
            latest_searches = []
            try:
                latest_searches = stats.get_latest(limit=5)
            except PyMongoError as e:
                print(f"{RED}Ошибка MongoDB: {e}{RESET}")
            except Exception as e:
                print(f"{RED}Непредвиденная ошибка: {e}{RESET}")

            for i, entry in enumerate(latest_searches, 1):
                search_type = get_search_description(entry['search_type'])
                params = entry['params']
                print(f"{i}. {search_type}: {params}")


        elif choice == 4:
            try:
                actor = input("Enter actor name: ")
                all_results = db.search_by_actor(actor, limit=1000)
            except ProgrammingError as e:
                print(f"{RED}Ошибка в SQL-запросе: {e}{RESET}")
                continue
            except OperationalError as e:
                print(f"{RED}Ошибка подключения к базе данных: {e}{RESET}")
                continue
            except MySQLError as e:
                print(f"{RED}Ошибка MySQL: {e}{RESET}")
                continue
            except Exception as e:
                print(f"{RED}Непредвиденная ошибка: {e}{RESET}")
                continue

            def description_func(entry):
                return f"{entry['title']} ({entry['release_year']}) - {entry['actor_name']}"
            print_paginated_results(all_results, description_func, limit=10)
            logger.log_search("by actor", {"actor": actor}, len(all_results))

        elif choice == 5:
            print(f"{MAGENTA}Goodbye! See you soon.{RESET}")
            db.close()
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Программа остановлена пользователем.{RESET}")
    except Exception as e:
        print(f"\n{RED}Произошла ошибка: {e}{RESET}")




