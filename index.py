import sys
import requests
from pymongo import MongoClient
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox,
    QDialog, QTextEdit, QGridLayout, QTabWidget, QComboBox
)
import re

# Настройки
API_URL = 'http://localhost:3000/'  # Адрес вашего json-server
MONGO_URI = 'mongodb://localhost:27017/'  # Адрес MongoDB
DB_NAME = 'movie_app'
WATCHLIST_COLLECTION = 'watchlist'

# Подключение к MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
watchlist_collection = db[WATCHLIST_COLLECTION]

class MovieDetailsDialog(QDialog):
    """Окно с подробной информацией о фильме/сериале"""
    def __init__(self, content_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Информация: {content_data['title']}")
        
        layout = QGridLayout()
        
        # Отображение названия
        title_label = QLabel("Название:")
        layout.addWidget(title_label, 0, 0)
        title_value = QLabel(content_data.get('title', 'N/A'))
        layout.addWidget(title_value, 0, 1)
        
        # Отображение описания
        description_label = QLabel("Описание:")
        layout.addWidget(description_label, 1, 0)
        description_value = QTextEdit(content_data.get('description', 'N/A'))
        description_value.setReadOnly(True)
        layout.addWidget(description_value, 1, 1)
        
        # Отображение рейтинга
        rating_label = QLabel("Рейтинг:")
        layout.addWidget(rating_label, 2, 0)
        rating_value = QLabel(str(content_data.get('rating', 'N/A')))
        layout.addWidget(rating_value, 2, 1)
        
        # Отображение актеров
        actors_label = QLabel("Актеры:")
        layout.addWidget(actors_label, 3, 0)
        actors_value = QLabel(", ".join(content_data.get('actors', ['N/A'])))
        layout.addWidget(actors_value, 3, 1)
        
        # Отображение жанров
        genres_label = QLabel("Жанры:")
        layout.addWidget(genres_label, 4, 0)
        genres_value = QLabel(", ".join(content_data.get('genres', ['N/A'])))
        layout.addWidget(genres_value, 4, 1)
        
        self.setLayout(layout)

class MovieApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie & Series App")
        self.setGeometry(100, 100, 600, 400)
        
        # Основной layout
        layout = QVBoxLayout()
        
        # Выбор типа контента (фильм/сериал)
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(["Фильмы", "Сериалы"])
        layout.addWidget(self.content_type_combo)
        
        # Поле для поиска
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Введите название, актера или жанр...")
        layout.addWidget(self.search_input)
        
        # Кнопка поиска
        self.search_button = QPushButton("Поиск", self)
        self.search_button.clicked.connect(self.search_content)
        layout.addWidget(self.search_button)
        
        # Вкладки для результатов и списка "Хочу посмотреть"
        self.tabs = QTabWidget()
        
        # Вкладка результатов поиска
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.show_content_details)  # Добавляем обработчик двойного клика
        self.tabs.addTab(self.results_list, "Результаты поиска")
        
        # Вкладка "Хочу посмотреть"
        self.watchlist_list = QListWidget()
        self.tabs.addTab(self.watchlist_list, "Хочу посмотреть")
        
        layout.addWidget(self.tabs)
        
        # Кнопка добавления в "Хочу посмотреть"
        self.add_to_watchlist_button = QPushButton("Добавить в 'Хочу посмотреть'", self)
        self.add_to_watchlist_button.clicked.connect(self.add_to_watchlist)
        layout.addWidget(self.add_to_watchlist_button)
        
        # Кнопка обновления списка рекомендаций
        self.recommendations_button = QPushButton("Получить рекомендации", self)
        self.recommendations_button.clicked.connect(self.get_recommendations)
        layout.addWidget(self.recommendations_button)
        
        # Установка основного виджета
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Загрузка списка "Хочу посмотреть" при запуске
        self.load_watchlist()

    def search_content(self):
        """Поиск контента по названию, актерам или жанрам"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите запрос для поиска.")
            return
        
        content_type = self.content_type_combo.currentText().lower()
        response = requests.get(f"{API_URL}{content_type}", params={'q': query.lower()})
        if response.status_code == 200:
            self.results_list.clear()
            contents = response.json()
            for content in contents:
                self.results_list.addItem(f"{content['title']} ({', '.join(content.get('genres', ['N/A']))})")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось выполнить поиск.")

    def add_to_watchlist(self):
        """Добавление контента в список 'Хочу посмотреть'"""
        selected_item = self.results_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите контент из списка.")
            return
        content_title = selected_item.text().split('(')[0].strip()
        
        # Проверяем, есть ли уже такой контент в списке
        existing_content = watchlist_collection.find_one({'title': {'$regex': re.escape(content_title), '$options': 'i'}})
        if existing_content:
            QMessageBox.warning(self, "Ошибка", "Этот контент уже в списке 'Хочу посмотреть'.")
            return
        
        # Добавление контента в MongoDB
        content_data = {'title': content_title, 'type': self.content_type_combo.currentText(), 'watched': False}
        result = watchlist_collection.insert_one(content_data)
        if result.inserted_id:
            self.load_watchlist()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить контент в список.")

    def load_watchlist(self):
        """Загрузка списка 'Хочу посмотреть' из MongoDB"""
        self.watchlist_list.clear()  # Очистка списка
        watchlist_contents = watchlist_collection.find({'watched': False})  # Получение записей из MongoDB
        for content in watchlist_contents:  # Перебор записей
            # Проверяем наличие поля 'type' и используем значение по умолчанию, если его нет
            content_type = content.get('type', 'N/A')
            self.watchlist_list.addItem(f"{content['title']} ({content_type})")  # Добавление записи в список

    def get_recommendations(self):
        """Получение рекомендаций"""
        watchlist_contents = list(watchlist_collection.find({'watched': False}))
        
        # Собираем все уникальные жанры из списка "Хочу посмотреть"
        genres = set()
        for content in watchlist_contents:
            if 'genres' in content and isinstance(content['genres'], list):
                genres.update(content['genres'])
        
        if not genres:
            QMessageBox.information(self, "Рекомендации", "Недостаточно данных для рекомендаций (добавьте контент с жанрами).")
            return
        
        recommendations = []
        for genre in genres:
            for content_type in ["movies", "series"]:
                response = requests.get(f"{API_URL}{content_type}", params={'genres_like': genre})
                if response.status_code == 200:
                    contents = response.json()
                    for content in contents:
                        # Исключаем контент, который уже есть в списке "Хочу посмотреть"
                        if not watchlist_collection.find_one({'title': content['title']}):
                            recommendations.append(content)
        
        if recommendations:
            recommended_content = recommendations[0]
            QMessageBox.information(
                self, "Рекомендации", 
                f"Рекомендуем: {recommended_content['title']}\n"
                f"Тип: {recommended_content.get('type', 'N/A')}\n"
                f"Жанр: {', '.join(recommended_content.get('genres', ['N/A']))}\n"
                f"Рейтинг: {recommended_content.get('rating', 'N/A')}"
            )
        else:
            QMessageBox.information(self, "Рекомендации", "Нет подходящих рекомендаций.")

    def show_content_details(self, item):
        """Отображение подробной информации о контенте"""
        content_title = item.text().split('(')[0].strip()
        content_type = self.content_type_combo.currentText().lower()
        
        # Ищем контент по названию через API
        response = requests.get(f"{API_URL}{content_type}", params={'title': content_title})
        if response.status_code == 200:
            contents = response.json()
            for content in contents:
                if content['title'] == content_title:
                    dialog = MovieDetailsDialog(content, self)
                    dialog.exec_()
                    break
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти информацию о контенте.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieApp()
    window.show()
    sys.exit(app.exec())