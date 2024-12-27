from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QVBoxLayout,
    QHBoxLayout, QGroupBox, QMessageBox, QDialog, QComboBox, QTableWidgetItem)
from game_redactor import EditGameForm
from db_manager import DatabaseManager

class GameCatalogForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Каталог игр')
        self.setMinimumSize(800, 600)

        # Поле поиска
        self.search_label = QLabel('Поиск:')
        self.search_input = QLineEdit()
        self.search_button = QPushButton('Искать')
        self.search_button.clicked.connect(self.search)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # Фильтры
        self.filter_group = QGroupBox('Фильтры')
        self.genre_label = QLabel('Жанр:')
        self.genre_combo = QComboBox()
        self.genre_combo.addItem("Не выбрано")
        self.year_label = QLabel('Год выхода:')
        self.year_combo = QComboBox()
        self.year_combo.addItem("Не выбрано")
        # коннектим сигналы комбобоксов к слоту
        self.genre_combo.currentIndexChanged.connect(self.apply_filters)
        self.year_combo.currentIndexChanged.connect(self.apply_filters)

        filter_layout = QVBoxLayout()
        filter_layout.addWidget(self.genre_label)
        filter_layout.addWidget(self.genre_combo)
        filter_layout.addWidget(self.year_label)
        filter_layout.addWidget(self.year_combo)
        self.filter_group.setLayout(filter_layout)

        # Кнопки навигации
        self.catalog_button = QPushButton('Каталог игр')
        self.catalog_button.clicked.connect(self.open_catalog_form)
        self.subscriptions_button = QPushButton('Редактирование подписок')
        self.subscriptions_button.clicked.connect(self.open_subscriptions_form)
        self.admin_button = QPushButton('Панель администратора')
        self.admin_button.clicked.connect(self.open_admin_panel_form)
        self.exit_button = QPushButton('Выход')
        self.exit_button.clicked.connect(self.close_form)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.catalog_button)
        nav_layout.addWidget(self.subscriptions_button)
        nav_layout.addWidget(self.admin_button)
        nav_layout.addWidget(self.exit_button)

        # Добавление игры
        self.add_game_button = QPushButton("Добавить игру")
        self.add_game_button.clicked.connect(self.add_game)

        # Таблица игр
        self.game_table = QTableWidget()
        self.game_table.setColumnCount(6)
        self.game_table.setHorizontalHeaderLabels(['Название', 'Жанр', 'Разработчик', 'Издатель', 'Год выхода', ''])
        self.game_table.setRowCount(0)
        self.game_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Инициализируем DatabaseManager
        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        # Загружаем данные из БД при инициализации
        self.load_games_from_db()
        self.populate_filter_comboboxes()

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.filter_group)
        main_layout.addWidget(self.add_game_button)
        main_layout.addWidget(self.game_table)
        main_layout.addLayout(nav_layout)

    def populate_filter_comboboxes(self):
        # Заполняем комбобоксы уникальными значениями из БД
        self.genre_combo.clear()
        self.year_combo.clear()
        self.genre_combo.addItem("Не выбрано")
        self.year_combo.addItem("Не выбрано")

        genres = self.db_manager.execute_query("SELECT DISTINCT genre FROM Games")
        years = self.db_manager.execute_query("SELECT DISTINCT release_date FROM Games")

        for genre in genres:
            self.genre_combo.addItem(genre[0])
        for year in years:
            self.year_combo.addItem(str(year[0]))

    def add_game(self):
        # Создаем пустую форму редактирования игры и передаем ссылку на таблицу
        self.edit_game_form = EditGameForm(self, game_table=self.game_table)
        if self.edit_game_form.exec_() == QDialog.Accepted:
            self.load_games_from_db()
            self.populate_filter_comboboxes()

    def search(self):
        # При поиске просто вызываем apply_filters
        self.apply_filters()

    def apply_filters(self):
        # Применяем фильтры к таблице
        selected_genre = self.genre_combo.currentText()
        selected_year = self.year_combo.currentText()

        for row in range(self.game_table.rowCount()):
            genre_item = self.game_table.item(row, 1)
            year_item = self.game_table.item(row, 4)

            genre_match = selected_genre == "Не выбрано" or (genre_item and genre_item.text() == selected_genre)
            year_match = selected_year == "Не выбрано" or (year_item and year_item.text() == selected_year)

            self.game_table.setRowHidden(row, not (genre_match and year_match))

    def edit_game(self, row):
        game_data = {
            'name': self.game_table.item(row, 0).text(),
            'genre': self.game_table.item(row, 1).text(),
            'developer': self.game_table.item(row, 2).text(),
            'publisher': self.game_table.item(row, 3).text(),
            'year': self.game_table.item(row, 4).text(),
            'key': '',
            'description': '',
            'image_path': ''
        }
        # Создаем форму редактирования игры, передаем данные и ссылку на таблицу
        self.edit_game_form = EditGameForm(self, game_data, self.game_table)
        self.edit_game_form.exec_()

    def load_games_from_db(self):
        query = "SELECT title, genre, developer, publisher, release_date FROM Games"
        games = self.db_manager.execute_query(query)

        if games is not None:
            self.game_table.setRowCount(0)
            for row, game in enumerate(games):
                self.game_table.insertRow(row)
                self.game_table.setItem(row, 0, QTableWidgetItem(game[0]))
                self.game_table.setItem(row, 1, QTableWidgetItem(game[1]))
                self.game_table.setItem(row, 2, QTableWidgetItem(game[2]))
                self.game_table.setItem(row, 3, QTableWidgetItem(game[3]))
                self.game_table.setItem(row, 4, QTableWidgetItem(str(game[4])))

                # Создаем кнопки в шестом столбце
                button_layout = QHBoxLayout()
                edit_button = QPushButton('Изменить')
                delete_button = QPushButton('Удалить')
                edit_button.setMinimumHeight(20)
                delete_button.setMinimumHeight(20)
                button_layout.addWidget(edit_button)
                button_layout.addWidget(delete_button)
                # Центрируем кнопки в ячейке
                cell_widget = QWidget()
                cell_widget.setLayout(button_layout)
                self.game_table.setCellWidget(row, 5, cell_widget)

                edit_button.clicked.connect(lambda _, r=row: self.edit_game(r))
                delete_button.clicked.connect(lambda _, r=row: self.delete_game(r))

            self.game_table.resizeColumnsToContents()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные из БД.")

    def delete_game(self, row):
        title = self.game_table.item(row, 0).text()

        # Запрашиваем подтверждение удаления
        reply = QMessageBox.question(self, 'Удаление игры', f'Вы уверены, что хотите удалить игру "{title}"?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Удаляем запись из БД
            query = "DELETE FROM Games WHERE title = %s"
            if self.db_manager.execute_update(query, (title,)):
                # Удаляем строку из таблицы
                self.game_table.removeRow(row)
                QMessageBox.information(self, "Успех", f"Игра '{title}' успешно удалена.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить игру '{title}'.")

    def open_catalog_form(self):
        self.main_window.show_game_catalog_form()

    def open_subscriptions_form(self):
        self.main_window.show_subscription_catalog_form()

    def open_admin_panel_form(self):
        self.main_window.show_admin_panel_form()

    def close_form(self):
        self.main_window.close()