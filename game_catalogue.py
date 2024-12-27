from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QHBoxLayout, QCheckBox, QGroupBox, QMessageBox, QDialog)
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
        self.genre_checkbox = QCheckBox('Жанр')
        self.developer_checkbox = QCheckBox('Разработчик')
        self.publisher_checkbox = QCheckBox('Издатель')
        self.year_checkbox = QCheckBox('Год выхода')
        self.genre_checkbox.stateChanged.connect(self.filter_table)
        self.developer_checkbox.stateChanged.connect(self.filter_table)
        self.publisher_checkbox.stateChanged.connect(self.filter_table)
        self.year_checkbox.stateChanged.connect(self.filter_table)

        filter_layout = QVBoxLayout()
        filter_layout.addWidget(self.genre_checkbox)
        filter_layout.addWidget(self.developer_checkbox)
        filter_layout.addWidget(self.publisher_checkbox)
        filter_layout.addWidget(self.year_checkbox)
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

        # Инициализируем DatabaseManager
        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        # Загружаем данные из БД при инициализации
        self.load_games_from_db()

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.filter_group)
        main_layout.addWidget(self.add_game_button)
        main_layout.addWidget(self.game_table)
        main_layout.addLayout(nav_layout)

    def add_game(self):
        # Создаем пустую форму редактирования игры и передаем ссылку на таблицу
        self.edit_game_form = EditGameForm(self, game_table=self.game_table)
        if self.edit_game_form.exec_() == QDialog.Accepted:
            self.load_games_from_db()

    def search(self):
        search_text = self.search_input.text().lower()
        for row in range(self.game_table.rowCount()):
            item = self.game_table.item(row, 0)
            if search_text in item.text().lower():
                self.game_table.setRowHidden(row, False)
            else:
                self.game_table.setRowHidden(row, True)
        self.filter_table()

    def filter_table(self):
      for row in range(self.game_table.rowCount()):
          self.game_table.setRowHidden(row, False)

      search_text = self.search_input.text().lower()
      for row in range(self.game_table.rowCount()):
          item = self.game_table.item(row, 0)
          if search_text not in item.text().lower():
              self.game_table.setRowHidden(row, True)

      for row in range(self.game_table.rowCount()):
          if not self.game_table.isRowHidden(row):
              genre_match = not self.genre_checkbox.isChecked() or (self.game_table.item(row, 1) and self.genre_checkbox.text() == self.game_table.item(row, 1).text())
              developer_match = not self.developer_checkbox.isChecked() or (self.game_table.item(row, 2) and self.developer_checkbox.text() == self.game_table.item(row, 2).text())
              publisher_match = not self.publisher_checkbox.isChecked() or (self.game_table.item(row, 3) and self.publisher_checkbox.text() == self.game_table.item(row, 3).text())
              year_match = not self.year_checkbox.isChecked() or (self.game_table.item(row, 4) and self.year_checkbox.text() == self.game_table.item(row, 4).text())

              if not (genre_match and developer_match and publisher_match and year_match):
                  self.game_table.setRowHidden(row, True)

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
            self.game_table.setRowCount(len(games))
            for row, game in enumerate(games):
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

                edit_button.clicked.connect(lambda _, row=row: self.edit_game(row))
                delete_button.clicked.connect(lambda _, row=row: self.delete_game(row))

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