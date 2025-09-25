from db_connector import DBConnector
from log_writer import LogSearch
from formatter import GREEN, MAGENTA, RESET, BERUSA
from log_stats import LogStats  # Добавляем импорт

def main_menu():
    print(f"{MAGENTA}\n*** WELCOME TO FILM SEARCH ***{RESET}")
    print("Choose search type:")
    print("1. Search by title")
    print("2. Search by genre and years")
    print("3. Search for popular queries")
    print("4. Search by actor")
    print("5. Exit")

    while True:
        try:
            choice = int(input(f"{GREEN}Your choice: {RESET}"))
            if choice in range(1, 6):
                return choice
            else:
                print(f"{BERUSA}Please choose a number between 1 and 5.{RESET}")
        except ValueError:
            print(f"{BERUSA}Invalid input. Enter a number.{RESET}")

def main():
    db = DBConnector()
    logger = LogSearch()
    stats = LogStats(logger)  # Создаём объект статистики

    while True:
        choice = main_menu()

        if choice == 1:
            title = input("Enter film title: ")
            results = db.search_by_title(title)
            logger.log_search("by title", {"title": title}, len(results))
            for film in results:
                print(f"- {film['title']}")

        elif choice == 2:
            genres = db.get_all_genres()
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
                year_from = int(input("Year from: "))
                year_to = int(input("Year to: "))
                results = db.search_by_genre_and_years(genre, year_from, year_to)
                logger.log_search("by genre and years", {"genre": genre, "from": year_from, "to": year_to}, len(results))
                for film in results:
                    print(f"- {film['title']} ({film['release_year']}) - {film['genre']}")
            except ValueError:
                print(f"{BERUSA}Invalid year input.{RESET}")

        elif choice == 3:
            print(f"{MAGENTA}Top popular searches:{RESET}")
            popular = stats.get_popular(limit=5)
            for i, entry in enumerate(popular, 1):
                print(f"{i}. Type: {entry['search_type']} | Params: {entry['params']} | Count: {entry['count']}")

        elif choice == 4:
            actor = input("Enter actor name: ")
            results = db.search_by_actor(actor)
            logger.log_search("by actor", {"actor": actor}, len(results))
            for film in results:
                print(f"- {film['title']} ({film['release_year']}) - {film['actor_name']}")

        elif choice == 5:
            print(f"{MAGENTA}Goodbye! See you soon.{RESET}")
            db.close()
            break

if __name__ == "__main__":
    main()



# from db_connector import DBConnector
# from log_writer import LogSearch
# from formatter import GREEN, MAGENTA, RESET, BERUSA
#
# def main_menu():
#     print(f"{MAGENTA}\n*** WELCOME TO FILM SEARCH ***{RESET}")
#     print("Choose search type:")
#     print("1. Search by title")
#     print("2. Search by genre")
#     print("3. Search by year range")
#     print("4. Search by genre and years")
#     print("5. Search by actor")
#     print("6. Exit")
#
#     while True:
#         try:
#             choice = int(input(f"{GREEN}Your choice: {RESET}"))
#             if choice in range(1, 7):
#                 return choice
#             else:
#                 print(f"{BERUSA}Please choose a number between 1 and 6.{RESET}")
#         except ValueError:
#             print(f"{BERUSA}Invalid input. Enter a number.{RESET}")
#
# def main():
#     db = DBConnector()
#     logger = LogSearch()
#
#     while True:
#         choice = main_menu()
#
#         if choice == 1:
#             title = input("Enter film title: ")
#             results = db.search_by_title(title)
#             logger.log_search("by title", {"title": title}, len(results))
#             for film in results:
#                 print(f"- {film['title']}")
#
#         elif choice == 2:
#             genres = db.get_all_genres()
#             print("Available genres:")
#             for i, genre in enumerate(genres, 1):
#                 print(f"{i}. {genre}")
#
#             genre_input = input("Choose genre (number or name): ").strip()
#
#             if genre_input.isdigit():
#                 index = int(genre_input) - 1
#                 if index not in range(len(genres)):
#                     print(f"{BERUSA}Invalid selection.{RESET}")
#                     continue
#                 genre = genres[index]
#             else:
#                 genre_matches = [g for g in genres if g.lower() == genre_input.lower()]
#                 if not genre_matches:
#                     print(f"{BERUSA}Genre not found.{RESET}")
#                     continue
#                 genre = genre_matches[0]
#
#             results = db.search_by_genre(genre)
#             logger.log_search("by genre", {"genre": genre}, len(results))
#             for film in results:
#                 print(f"- {film['title']} ({film['release_year']})")
#
#         elif choice == 3:
#             try:
#                 year_from = int(input("Year from: "))
#                 year_to = int(input("Year to: "))
#                 results = db.search_by_year_range(year_from, year_to)
#                 logger.log_search("by years (from... to...)", {"from": year_from, "to": year_to}, len(results))
#                 for film in results:
#                     print(f"- {film['title']} ({film['release_year']})")
#             except ValueError:
#                 print(f"{BERUSA}Invalid year input.{RESET}")
#
#         elif choice == 4:
#             try:
#                 genre = input("Enter genre: ")
#                 year_from = int(input("Year from: "))
#                 year_to = int(input("Year to: "))
#                 results = db.search_by_genre_and_years(genre, year_from, year_to)
#                 logger.log_search("by genre and years", {"genre": genre, "from": year_from, "to": year_to}, len(results))
#                 for film in results:
#                     print(f"- {film['title']} ({film['release_year']}) - {film['genre']}")
#             except ValueError:
#                 print(f"{BERUSA}Invalid input.{RESET}")
#
#         elif choice == 5:
#             actor = input("Enter actor name: ")
#             results = db.search_by_actor(actor)
#             logger.log_search("by actor", {"actor": actor}, len(results))
#             for film in results:
#                 print(f"- {film['title']} ({film['release_year']}) - {film['actor_name']}")
#
#         elif choice == 6:
#             print(f"{MAGENTA}Goodbye! See you soon.{RESET}")
#             db.close()
#             break
#
# if __name__ == "__main__":
#     main()



# from db_connector import DBConnector
# from log_writer import LogSearch
# from formatter import GREEN, MAGENTA, RESET, BERUSA
#
# def main_menu():
#     print(f"{MAGENTA}\n*** WELCOME TO FILM SEARCH ***{RESET}")
#     print("Choose search type:")
#     print("1. Search by title")
#     print("2. Search by year range")
#     print("3. Search by genre and years")
#     print("4. Search by actor")
#     print("5. Exit")
#
#     while True:
#         try:
#             choice = int(input(f"{GREEN}Your choice: {RESET}"))
#             if choice in range(1, 6):
#                 return choice
#             else:
#                 print(f"{BERUSA}Please choose a number between 1 and 5.{RESET}")
#         except ValueError:
#             print(f"{BERUSA}Invalid input. Enter a number.{RESET}")
#
# def main():
#     db = DBConnector()
#     logger = LogSearch()
#
#     while True:
#         choice = main_menu()
#
#         if choice == 1:
#             title = input("Enter film title: ")
#             results = db.search_by_title(title)
#             logger.log_search("by title", {"title": title}, len(results))
#             for film in results:
#                 print(f"- {film['title']}")
#
#         elif choice == 2:
#             try:
#                 year_from = int(input("Year from: "))
#                 year_to = int(input("Year to: "))
#                 results = db.search_by_year_range(year_from, year_to)
#                 logger.log_search("by years", {"from": year_from, "to": year_to}, len(results))
#                 for film in results:
#                     print(f"- {film['title']} ({film['release_year']})")
#             except ValueError:
#                 print(f"{BERUSA}Invalid year input.{RESET}")
#
#         elif choice == 3:
#             genres = db.get_all_genres()
#             print("Available genres:")
#             for i, genre in enumerate(genres, 1):
#                 print(f"{i}. {genre}")
#
#             genre_input = input("Choose genre (number or name): ").strip()
#
#             if genre_input.isdigit():
#                 index = int(genre_input) - 1
#                 if index not in range(len(genres)):
#                     print(f"{BERUSA}Invalid selection.{RESET}")
#                     continue
#                 genre = genres[index]
#             else:
#                 genre_matches = [g for g in genres if g.lower() == genre_input.lower()]
#                 if not genre_matches:
#                     print(f"{BERUSA}Genre not found.{RESET}")
#                     continue
#                 genre = genre_matches[0]
#
#             try:
#                 year_from = int(input("Year from: "))
#                 year_to = int(input("Year to: "))
#                 results = db.search_by_genre_and_years(genre, year_from, year_to)
#                 logger.log_search("by genre and years", {"genre": genre, "from": year_from, "to": year_to}, len(results))
#                 for film in results:
#                     print(f"- {film['title']} ({film['release_year']}) - {film['genre']}")
#             except ValueError:
#                 print(f"{BERUSA}Invalid input.{RESET}")
#
#         elif choice == 4:
#             actor = input("Enter actor name: ")
#             results = db.search_by_actor(actor)
#             logger.log_search("by actor", {"actor": actor}, len(results))
#             for film in results:
#                 print(f"- {film['title']} ({film['release_year']}) - {film['actor_name']}")
#
#         elif choice == 5:
#             print(f"{MAGENTA}Goodbye! See you soon.{RESET}")
#             db.close()
#             break
#
# if __name__ == "__main__":
#     main()