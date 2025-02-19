import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QListWidget, QLabel, QTabWidget, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt


class MediaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Finder")
        self.setGeometry(100, 100, 800, 600)

        # Список "Хочу посмотреть"
        self.to_watch_movies = []
        self.to_watch_series = []

        # Главный виджет и layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Вкладки
        self.tabs = QTabWidget()
        self.movie_tab = QWidget()
        self.series_tab = QWidget()
        self.to_watch_tab = QWidget()  # Вкладка "Хочу посмотреть"
        self.recommendations_tab = QWidget()  # Новая вкладка "Рекомендации"
        self.tabs.addTab(self.movie_tab, "Фильмы")
        self.tabs.addTab(self.series_tab, "Сериалы")
        self.tabs.addTab(self.to_watch_tab, "Хочу посмотреть")
        self.tabs.addTab(self.recommendations_tab, "Рекомендации")

        # Настройка вкладок
        self.setup_movie_tab()
        self.setup_series_tab()
        self.setup_to_watch_tab()
        self.setup_recommendations_tab()  # Настройка новой вкладки

        # Добавляем вкладки в основной layout
        self.layout.addWidget(self.tabs)
        self.central_widget.setLayout(self.layout)

        # Загрузка всех фильмов и сериалов при старте
        self.load_all_movies()
        self.load_all_series()

        # Загрузка данных из TXT-файлов при запуске
        self.load_to_watch_from_file()
        self.update_to_watch_display()  # Обновляем отображение при старте
        self.update_recommendations()  # Обновляем рекомендации при старте

    def setup_movie_tab(self):
        layout = QVBoxLayout()

        # Поиск фильма
        search_layout = QHBoxLayout()
        self.movie_search_input = QLineEdit()
        self.movie_search_input.setPlaceholderText("Поиск фильма по названию, актерам или жанрам...")
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_movies)
        show_all_button = QPushButton("Показать все фильмы")
        show_all_button.clicked.connect(self.load_all_movies)
        search_layout.addWidget(self.movie_search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(show_all_button)

        # Результаты поиска
        self.movie_results = QListWidget()
        self.movie_results.itemClicked.connect(self.show_movie_details)

        # Детали фильма
        self.movie_details = QTextEdit()
        self.movie_details.setReadOnly(True)

        # Кнопка "Добавить в 'Хочу посмотреть'"
        self.add_movie_to_watchlist_button = QPushButton("Добавить в 'Хочу посмотреть'")
        self.add_movie_to_watchlist_button.clicked.connect(lambda: self.add_to_watch("movie"))

        # Добавляем элементы на вкладку
        layout.addLayout(search_layout)
        layout.addWidget(self.movie_results)
        layout.addWidget(self.movie_details)
        layout.addWidget(self.add_movie_to_watchlist_button)

        self.movie_tab.setLayout(layout)

    def setup_series_tab(self):
        layout = QVBoxLayout()

        # Поиск сериала
        search_layout = QHBoxLayout()
        self.series_search_input = QLineEdit()
        self.series_search_input.setPlaceholderText("Поиск сериала по названию, актерам или жанрам...")
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_series)
        show_all_button = QPushButton("Показать все сериалы")
        show_all_button.clicked.connect(self.load_all_series)
        search_layout.addWidget(self.series_search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(show_all_button)

        # Результаты поиска
        self.series_results = QListWidget()
        self.series_results.itemClicked.connect(self.show_series_details)

        # Детали сериала
        self.series_details = QTextEdit()
        self.series_details.setReadOnly(True)

        # Кнопка "Добавить в 'Хочу посмотреть'"
        self.add_series_to_watchlist_button = QPushButton("Добавить в 'Хочу посмотреть'")
        self.add_series_to_watchlist_button.clicked.connect(lambda: self.add_to_watch("series"))

        # Добавляем элементы на вкладку
        layout.addLayout(search_layout)
        layout.addWidget(self.series_results)
        layout.addWidget(self.series_details)
        layout.addWidget(self.add_series_to_watchlist_button)

        self.series_tab.setLayout(layout)

    def setup_to_watch_tab(self):
        layout = QVBoxLayout()

        # Отображение фильмов и сериалов
        self.to_watch_display = QTextEdit()
        self.to_watch_display.setReadOnly(True)

        # Добавляем элементы на вкладку
        layout.addWidget(self.to_watch_display)

        self.to_watch_tab.setLayout(layout)

    def setup_recommendations_tab(self):
        layout = QVBoxLayout()

        # Отображение рекомендаций
        self.recommendations_display = QTextEdit()
        self.recommendations_display.setReadOnly(True)

        # Добавляем элементы на вкладку
        layout.addWidget(self.recommendations_display)

        self.recommendations_tab.setLayout(layout)

    def load_all_movies(self):
        try:
            response = requests.get("http://localhost:3000/movies")
            data = response.json()

            if isinstance(data, list):
                movies = data
            elif isinstance(data, dict) and "movies" in data:
                movies = data["movies"]
            else:
                raise ValueError("Некорректная структура данных для фильмов")

            self.movie_results.clear()
            for movie in movies:
                self.movie_results.addItem(f"{movie['title']} ({', '.join(movie['genres'])})")
        except Exception as e:
            print(f"Ошибка при загрузке всех фильмов: {e}")

    def load_all_series(self):
        try:
            response = requests.get("http://localhost:3000/series")
            data = response.json()

            if isinstance(data, list):
                series = data
            elif isinstance(data, dict) and "series" in data:
                series = data["series"]
            else:
                raise ValueError("Некорректная структура данных для сериалов")

            self.series_results.clear()
            for s in series:
                self.series_results.addItem(f"{s['title']} ({', '.join(s['genres'])})")
        except Exception as e:
            print(f"Ошибка при загрузке всех сериалов: {e}")

    def add_to_watch(self, media_type):
        selected_item = None
        title = None

        if media_type == "movie":
            selected_item = self.movie_results.currentItem()
        elif media_type == "series":
            selected_item = self.series_results.currentItem()

        if not selected_item:
            return

        title = selected_item.text().split(" (")[0]

        # Проверяем, не добавлен ли уже элемент
        if media_type == "movie" and title in self.to_watch_movies:
            QMessageBox.warning(self, "Ошибка", f"Фильм '{title}' уже в списке 'Хочу посмотреть'.")
            return
        elif media_type == "series" and title in self.to_watch_series:
            QMessageBox.warning(self, "Ошибка", f"Сериал '{title}' уже в списке 'Хочу посмотреть'.")
            return

        # Добавляем в список
        if media_type == "movie":
            self.to_watch_movies.append(title)
        elif media_type == "series":
            self.to_watch_series.append(title)

        # Сохраняем в файл
        self.save_to_watch_to_file()

        # Обновляем отображение
        self.update_to_watch_display()
        self.update_recommendations()  # Обновляем рекомендации

        # Уведомляем пользователя
        QMessageBox.information(self, "Успех", f"'{title}' добавлен в 'Хочу посмотреть'.")

    def save_to_watch_to_file(self):
        # Сохраняем фильмы
        with open("to_watch_movies.txt", "w", encoding="utf-8") as movie_file:
            if self.to_watch_movies:
                movie_file.write("Фильмы:\n")
                for title in self.to_watch_movies:
                    movie_file.write(f"- {title}\n")
            else:
                movie_file.write("Фильмы: (пусто)\n")

        # Сохраняем сериалы
        with open("to_watch_series.txt", "w", encoding="utf-8") as series_file:
            if self.to_watch_series:
                series_file.write("Сериалы:\n")
                for title in self.to_watch_series:
                    series_file.write(f"- {title}\n")
            else:
                series_file.write("Сериалы: (пусто)\n")

    def load_to_watch_from_file(self):
        # Загружаем фильмы
        try:
            with open("to_watch_movies.txt", "r", encoding="utf-8") as movie_file:
                lines = movie_file.readlines()
                self.to_watch_movies = [line.strip()[2:] for line in lines if line.startswith("-")]
        except FileNotFoundError:
            pass  # Файл не существует, игнорируем ошибку

        # Загружаем сериалы
        try:
            with open("to_watch_series.txt", "r", encoding="utf-8") as series_file:
                lines = series_file.readlines()
                self.to_watch_series = [line.strip()[2:] for line in lines if line.startswith("-")]
        except FileNotFoundError:
            pass  # Файл не существует, игнорируем ошибку

    def update_to_watch_display(self):
        # Генерируем текст для отображения
        to_watch_text = "Фильмы:\n"
        if self.to_watch_movies:
            for title in self.to_watch_movies:
                to_watch_text += f"- {title}\n"
        else:
            to_watch_text += "(пусто)\n"

        to_watch_text += "\nСериалы:\n"
        if self.to_watch_series:
            for title in self.to_watch_series:
                to_watch_text += f"- {title}\n"
        else:
            to_watch_text += "(пусто)\n"

        # Обновляем отображение
        self.to_watch_display.setText(to_watch_text)

    def update_recommendations(self):
        # Собираем все жанры из "Хочу посмотреть"
        genres = set()
        for title in self.to_watch_movies:
            movie = self.find_movie_by_title(title)
            if movie:
                genres.update(movie["genres"])

        for title in self.to_watch_series:
            series = self.find_series_by_title(title)
            if series:
                genres.update(series["genres"])

        # Ищем рекомендации
        recommendations = self.find_recommendations_by_genres(genres)

        # Генерируем текст для отображения
        recommendations_text = "Рекомендации:\n"
        if recommendations:
            for item in recommendations:
                recommendations_text += f"- {item['title']} ({', '.join(item['genres'])})\n"
        else:
            recommendations_text += "(пусто)\n"

        # Обновляем отображение
        self.recommendations_display.setText(recommendations_text)

    def find_movie_by_title(self, title):
        try:
            response = requests.get("http://localhost:3000/movies")
            data = response.json()

            if isinstance(data, list):
                movies = data
            elif isinstance(data, dict) and "movies" in data:
                movies = data["movies"]
            else:
                return None

            return next((m for m in movies if m["title"] == title), None)
        except Exception as e:
            print(f"Ошибка при поиске фильма: {e}")
            return None

    def find_series_by_title(self, title):
        try:
            response = requests.get("http://localhost:3000/series")
            data = response.json()

            if isinstance(data, list):
                series = data
            elif isinstance(data, dict) and "series" in data:
                series = data["series"]
            else:
                return None

            return next((s for s in series if s["title"] == title), None)
        except Exception as e:
            print(f"Ошибка при поиске сериала: {e}")
            return None

    def find_recommendations_by_genres(self, genres):
        recommendations = []

        try:
            # Ищем фильмы
            response_movies = requests.get("http://localhost:3000/movies")
            data_movies = response_movies.json()

            if isinstance(data_movies, list):
                movies = data_movies
            elif isinstance(data_movies, dict) and "movies" in data_movies:
                movies = data_movies["movies"]
            else:
                movies = []

            for movie in movies:
                if any(genre in movie["genres"] for genre in genres) and movie["title"] not in self.to_watch_movies:
                    recommendations.append(movie)

            # Ищем сериалы
            response_series = requests.get("http://localhost:3000/series")
            data_series = response_series.json()

            if isinstance(data_series, list):
                series = data_series
            elif isinstance(data_series, dict) and "series" in data_series:
                series = data_series["series"]
            else:
                series = []

            for s in series:
                if any(genre in s["genres"] for genre in genres) and s["title"] not in self.to_watch_series:
                    recommendations.append(s)

        except Exception as e:
            print(f"Ошибка при поиске рекомендаций: {e}")

        return recommendations

    def search_movies(self):
        query = self.movie_search_input.text().lower()
        if not query:
            return

        try:
            response = requests.get("http://localhost:3000/movies")
            data = response.json()

            if isinstance(data, list):
                movies = data
            elif isinstance(data, dict) and "movies" in data:
                movies = data["movies"]
            else:
                raise ValueError("Некорректная структура данных для фильмов")

            filtered_movies = [
                movie for movie in movies
                if query in movie["title"].lower() or
                   any(query in actor.lower() for actor in movie["actors"]) or
                   any(query in genre.lower() for genre in movie["genres"])
            ]
            self.movie_results.clear()
            for movie in filtered_movies:
                self.movie_results.addItem(f"{movie['title']} ({', '.join(movie['genres'])})")
        except Exception as e:
            print(f"Ошибка при поиске фильмов: {e}")

    def show_movie_details(self, item):
        title = item.text().split(" (")[0]
        try:
            response = requests.get("http://localhost:3000/movies")
            data = response.json()

            if isinstance(data, list):
                movies = data
            elif isinstance(data, dict) and "movies" in data:
                movies = data["movies"]
            else:
                raise ValueError("Некорректная структура данных для фильмов")

            movie = next((m for m in movies if m["title"] == title), None)
            if movie:
                details = (
                    f"Название: {movie['title']}\n"
                    f"Описание: {movie['description']}\n"
                    f"Рейтинг: {movie['rating']}\n"
                    f"Актеры: {', '.join(movie['actors'])}\n"
                    f"Жанры: {', '.join(movie['genres'])}"
                )
                self.movie_details.setText(details)
        except Exception as e:
            print(f"Ошибка при получении деталей фильма: {e}")

    def search_series(self):
        query = self.series_search_input.text().lower()
        if not query:
            return

        try:
            response = requests.get("http://localhost:3000/series")
            data = response.json()

            if isinstance(data, list):
                series = data
            elif isinstance(data, dict) and "series" in data:
                series = data["series"]
            else:
                raise ValueError("Некорректная структура данных для сериалов")

            filtered_series = [
                s for s in series
                if query in s["title"].lower() or
                   any(query in actor.lower() for actor in s["actors"]) or
                   any(query in genre.lower() for genre in s["genres"])
            ]
            self.series_results.clear()
            for s in filtered_series:
                self.series_results.addItem(f"{s['title']} ({', '.join(s['genres'])})")
        except Exception as e:
            print(f"Ошибка при поиске сериалов: {e}")

    def show_series_details(self, item):
        title = item.text().split(" (")[0]
        try:
            response = requests.get("http://localhost:3000/series")
            data = response.json()

            if isinstance(data, list):
                series = data
            elif isinstance(data, dict) and "series" in data:
                series = data["series"]
            else:
                raise ValueError("Некорректная структура данных для сериалов")

            s = next((s for s in series if s["title"] == title), None)
            if s:
                details = (
                    f"Название: {s['title']}\n"
                    f"Описание: {s['description']}\n"
                    f"Рейтинг: {s['rating']}\n"
                    f"Актеры: {', '.join(s['actors'])}\n"
                    f"Жанры: {', '.join(s['genres'])}"
                )
                self.series_details.setText(details)
        except Exception as e:
            print(f"Ошибка при получении деталей сериала: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MediaApp()
    window.show()
    sys.exit(app.exec())