from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit,
                             QFileDialog, QMessageBox, QDialog, QTableWidgetItem)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class EditGameForm(QDialog):
    def __init__(self, parent, game_data=None, game_table=None):
        super().__init__(parent)
        self.setWindowTitle('Редактирование игры')
        self.setMinimumSize(400, 500)
        self.game_data = game_data
        self.game_table = game_table

        self.name_label = QLabel('Название игры:')
        self.name_input = QLineEdit()

        self.genre_label = QLabel('Жанр:')
        self.genre_input = QLineEdit()

        self.developer_label = QLabel('Разработчик:')
        self.developer_input = QLineEdit()

        self.publisher_label = QLabel('Издатель:')
        self.publisher_input = QLineEdit()

        self.year_label = QLabel('Год выхода:')
        self.year_input = QLineEdit()

        self.description_label = QLabel('Описание:')
        self.description_input = QTextEdit()

        # Область для изображения
        self.image_display = QLabel()
        self.image_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.image_display.setText("Область для изображений игры")
        self.image_display.mousePressEvent = self.add_image

        self.key_label = QLabel('Ключ (AAAA-AAAA-AAAA-AAAA):')
        self.key_input = QLineEdit()
        self.key_input.setInputMask('AAAA-AAAA-AAAA-AAAA;_')

        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.save_game)
        self.cancel_button = QPushButton('Вернуться')
        self.cancel_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.image_display)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.genre_label)
        layout.addWidget(self.genre_input)
        layout.addWidget(self.developer_label)
        layout.addWidget(self.developer_input)
        layout.addWidget(self.publisher_label)
        layout.addWidget(self.publisher_input)
        layout.addWidget(self.year_label)
        layout.addWidget(self.year_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.key_label)
        layout.addWidget(self.key_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        self.image_path = ""

        if self.game_data:
            self.set_game_data(self.game_data)

    def add_image(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Выберите изображение', '', 'Image Files (*.png *.jpg *.bmp)')
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.image_display.setPixmap(pixmap.scaledToWidth(self.width()))
                self.image_display.setScaledContents(True)
                self.image_display.setText("")
                self.image_path = file_path
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить изображение.')
                self.image_path = ""  # Обнуление пути

    def save_game(self):
        if not all([self.name_input.text(), self.genre_input.text(), self.developer_input.text(),
                    self.publisher_input.text(), self.year_input.text(), self.key_input.text()]):
            QMessageBox.warning(self, 'Предупреждение', 'Пожалуйста, заполните все поля, кроме описания и изображения.')
            return

        game_data = {
            'name': self.name_input.text(),
            'genre': self.genre_input.text(),
            'developer': self.developer_input.text(),
            'publisher': self.publisher_input.text(),
            'year': self.year_input.text(),
            'description': self.description_input.toPlainText(),
            'image_path': self.image_path,
            'key': self.key_input.text()
        }

        parent_form = self.parent()
        from game_catalogue import GameCatalogForm
        if isinstance(parent_form, GameCatalogForm):
            if self.game_data:  # Редактирование существующей игры
                # Формируем запрос на обновление данных
                query = """
                    UPDATE Games 
                    SET genre = %s, 
                        developer = %s, 
                        publisher = %s, 
                        release_date = %s, 
                        description = %s, 
                        game_key = %s
                    WHERE title = %s
                """
                params = (
                    game_data['genre'],
                    game_data['developer'],
                    game_data['publisher'],
                    game_data['year'],
                    game_data['description'],
                    game_data['key'],
                    game_data['name']
                )
                # Выполняем запрос на обновление
                rows_affected = parent_form.db_manager.execute_update(query, params)
                if rows_affected == 0:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные игры.")
                else:
                    # Обновляем данные в таблице
                    row_index = -1
                    for i in range(parent_form.game_table.rowCount()):
                        if parent_form.game_table.item(i, 0).text() == self.game_data['name']:
                            row_index = i
                            break
                    if row_index != -1:
                        parent_form.game_table.setItem(row_index, 0, QTableWidgetItem(game_data['name']))
                        parent_form.game_table.setItem(row_index, 1, QTableWidgetItem(game_data['genre']))
                        parent_form.game_table.setItem(row_index, 2, QTableWidgetItem(game_data['developer']))
                        parent_form.game_table.setItem(row_index, 3, QTableWidgetItem(game_data['publisher']))
                        parent_form.game_table.setItem(row_index, 4, QTableWidgetItem(game_data['year']))
                        parent_form.game_table.resizeColumnsToContents()

            else:  # Добавление новой игры
                # Формируем запрос на вставку данных
                query = """
                    INSERT INTO Games (title, genre, developer, publisher, release_date, description, game_key)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    game_data['name'],
                    game_data['genre'],
                    game_data['developer'],
                    game_data['publisher'],
                    game_data['year'],
                    game_data['description'],
                    game_data['key']
                )

                res = parent_form.db_manager.execute_query(query, params, fetch_all=False)
                # Выполняем запрос на вставку
                if res is None:
                    parent_form.game_table.insertRow(parent_form.game_table.rowCount())
                    parent_form.game_table.setItem(parent_form.game_table.rowCount() - 1, 0, QTableWidgetItem(game_data['name']))
                    parent_form.game_table.setItem(parent_form.game_table.rowCount() - 1, 1, QTableWidgetItem(game_data['genre']))
                    parent_form.game_table.setItem(parent_form.game_table.rowCount() - 1, 2, QTableWidgetItem(game_data['developer']))
                    parent_form.game_table.setItem(parent_form.game_table.rowCount() - 1, 3, QTableWidgetItem(game_data['publisher']))
                    parent_form.game_table.setItem(parent_form.game_table.rowCount() - 1, 4, QTableWidgetItem(game_data['year']))
                    edit_button = QPushButton('Изменить')
                    edit_button.clicked.connect(lambda _, row=(parent_form.game_table.rowCount() - 1): parent_form.edit_game(row))
                    parent_form.game_table.setCellWidget(parent_form.game_table.rowCount() - 1, 5, edit_button)
                    parent_form.game_table.resizeColumnsToContents()
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить игру в базу данных.")

        self.close()

    def set_game_data(self, game_data):
        if game_data:
            self.name_input.setText(game_data['name'])
            self.genre_input.setText(game_data['genre'])
            self.developer_input.setText(game_data['developer'])
            self.publisher_input.setText(game_data['publisher'])
            self.year_input.setText(game_data['year'])
            self.key_input.setText(game_data['key'])
            self.description_input.setText(game_data['description'])
            if game_data['image_path']:
                pixmap = QPixmap(game_data['image_path'])
                if not pixmap.isNull():
                    self.image_display.setPixmap(pixmap.scaledToWidth(self.width()))
                    self.image_display.setScaledContents(True)
                    self.image_display.setText("")
                    self.image_path = game_data['image_path']
                else:
                    self.image_display.setText("Изображение не найдено")
                    self.image_path = ""
            else:
                self.image_display.setText("Область для изображений игры")
                self.image_path = ""