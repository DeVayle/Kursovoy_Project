from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout,
                             QFormLayout, QMessageBox, QHBoxLayout, QListWidget, QAbstractItemView, QListWidgetItem)
from db_manager import DatabaseManager


class EditSubscriptionForm(QDialog):
    def __init__(self, parent, plan_data=None):
        super().__init__(parent)
        self.setWindowTitle('Редактирование подписки')
        self.setMinimumSize(600, 400)
        self.plan_data = plan_data
        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        # Поля формы
        self.plan_name_label = QLabel('Название подписки')
        self.plan_name_input = QLineEdit()
        self.price_label = QLabel('Цена подписки')
        self.price_input = QLineEdit()

        main_form_layout = QHBoxLayout()
        left_form_layout = QFormLayout()
        left_form_layout.addRow(self.plan_name_label, self.plan_name_input)
        left_form_layout.addRow(self.price_label, self.price_input)

        self.description_label = QLabel('Описание подписки\n(возможные преимущества)')
        self.description_input = QTextEdit()
        self.duration_label = QLabel('Длительность (в днях):')
        self.duration_input = QLineEdit()

        # Список игр в подписке
        self.games_in_subscription_label = QLabel('Список игр, доступных в подписке')
        self.games_in_subscription_list = QListWidget()
        self.games_in_subscription_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Кнопки для добавления и удаления игр
        self.add_game_button = QPushButton("Добавить игру")
        self.add_game_button.clicked.connect(self.add_game_to_subscription)
        self.remove_game_button = QPushButton("Удалить")
        self.remove_game_button.clicked.connect(self.remove_game_from_subscription)

        # Блокируем кнопки при создании новой подписки
        if not self.plan_data:
            self.add_game_button.setEnabled(False)
            self.remove_game_button.setEnabled(False)

        right_form_layout = QVBoxLayout()
        right_form_layout.addWidget(self.games_in_subscription_label)
        right_form_layout.addWidget(self.games_in_subscription_list)
        games_buttons_layout = QHBoxLayout()
        games_buttons_layout.addWidget(self.add_game_button)
        games_buttons_layout.addWidget(self.remove_game_button)
        right_form_layout.addLayout(games_buttons_layout)

        main_form_layout.addLayout(left_form_layout)
        main_form_layout.addLayout(right_form_layout)

        # Кнопки
        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.save_subscription)
        self.cancel_button = QPushButton('Вернуться')
        self.cancel_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addLayout(main_form_layout)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        if self.plan_data:
            self.set_plan_data(self.plan_data)
            self.load_games_in_subscription()

    def add_game_to_subscription(self):
        # Получаем список текущих игр в подписке
        current_games = [self.games_in_subscription_list.item(i).data(1) for i in
                         range(self.games_in_subscription_list.count())]

        add_game_form = AddGameToSubscriptionForm(self, self.plan_data['plan_id'], current_games)
        if add_game_form.exec_() == QDialog.Accepted:
            self.load_games_in_subscription()  # Обновляем список игр в подписке
            if self.parent() and self.parent().subscription_table.currentRow() >= 0:
                self.parent().show_games_in_subscription(self.parent().subscription_table.currentRow(), 0)

    def remove_game_from_subscription(self):
        selected_items = self.games_in_subscription_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите игру для удаления.")
            return

        # Получаем id подписки
        if self.plan_data and 'plan_id' in self.plan_data:
            plan_id = self.plan_data['plan_id']
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить ID подписки.")
            return

        for item in selected_items:
            game_id = item.data(1)  # Получаем game_id из скрытых данных

            # Удаляем игру из подписки в БД
            delete_query = "DELETE FROM gamesinplans WHERE plan_id = %s AND game_id = %s"
            if self.db_manager.execute_update(delete_query, (plan_id, game_id)):
                # Удаляем игру из списка на форме
                self.games_in_subscription_list.takeItem(self.games_in_subscription_list.row(item))
                # Перезагружаем список игр в подписке
                self.load_games_in_subscription()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить игру из подписки.")

        # Обновляем таблицу с играми в подписке, если родитель доступен
        if self.parent() and self.parent().subscription_table.currentRow() >= 0:
            self.parent().show_games_in_subscription(self.parent().subscription_table.currentRow(), 0)

    def load_games_in_subscription(self):
        self.games_in_subscription_list.clear()
        query = """
            SELECT g.title, g.game_id
            FROM games g
            JOIN gamesinplans gp ON g.game_id = gp.game_id
            WHERE gp.plan_id = %s
        """
        games = self.db_manager.execute_query(query, (self.plan_data['plan_id'],))
        if games:
            for title, game_id in games:
                item = QListWidgetItem(title)
                item.setData(1, game_id)  # Сохраняем game_id в скрытых данных
                self.games_in_subscription_list.addItem(item)

    def save_subscription(self):
        plan_data = {
            'plan_name': self.plan_name_input.text(),
            'description': self.description_input.toPlainText(),
            'price': self.price_input.text(),
            'duration_up_to': self.duration_input.text()
        }

        if not all(plan_data.values()):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля!')
            return

        if self.plan_data:  # Если данные существуют, редактируем
            query = """
                UPDATE plans 
                SET plan_name = %s, description = %s, price = %s, duration_up_to = %s 
                WHERE plan_id = %s
            """
            params = (
                plan_data['plan_name'],
                plan_data['description'],
                plan_data['price'],
                plan_data['duration_up_to'],
                self.plan_data['plan_id']
            )
            rows_affected = self.db_manager.execute_update(query, params)
            if rows_affected >= 0:
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные подписки.")
        else:  # Если данных нет, добавляем новую подписку
            query = """
                INSERT INTO plans (plan_name, description, price, duration_up_to)
                VALUES (%s, %s, %s, %s)
            """
            params = (
                plan_data['plan_name'],
                plan_data['description'],
                plan_data['price'],
                plan_data['duration_up_to']
            )
            rows_affected = self.db_manager.execute_update(query, params)

            if rows_affected > 0:
                # Получаем сгенерированный plan_id
                cursor = self.db_manager.cursor()
                cursor.execute("SELECT LAST_INSERT_ID()")
                result = cursor.fetchone()
                cursor.close()
                if result:
                    self.plan_data = {'plan_id': result[0]}
                    self.add_game_button.setEnabled(True)
                    self.remove_game_button.setEnabled(True)
                    # Обновляем таблицу в родительском окне
                    if self.parent():
                        self.parent().load_plans_from_db()
                    self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить подписку в базу данных.")

    def set_plan_data(self, plan_data):
        self.plan_name_input.setText(plan_data['plan_name'])
        self.description_input.setText(plan_data['description'])
        self.price_input.setText(plan_data['price'])
        self.duration_input.setText(plan_data['duration_up_to'])

class AddGameToSubscriptionForm(QDialog):
    def __init__(self, parent=None, plan_id=None, current_games=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить игру в подписку')
        self.setMinimumSize(400, 200)
        self.plan_id = plan_id
        self.current_games = current_games or []
        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        self.game_label = QLabel('Название игры:')
        self.game_input = QLineEdit()  # Изменено на QLineEdit

        self.add_button = QPushButton('Добавить')
        self.add_button.clicked.connect(self.add_game)

        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.game_label)
        layout.addWidget(self.game_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def add_game(self):
        game_title = self.game_input.text().strip()

        if not game_title:
            QMessageBox.warning(self, "Предупреждение", "Введите название игры.")
            return

        # Проверяем, есть ли игра с таким названием в БД
        query = "SELECT game_id FROM games WHERE title = %s"
        game_id = self.db_manager.execute_query(query, (game_title,), fetch_all=False)

        if game_id:
            game_id = game_id[0]
            # Проверяем, не добавлена ли уже эта игра в подписку
            if game_id in self.current_games:
                QMessageBox.warning(self, "Предупреждение", "Эта игра уже добавлена в подписку.")
                return

            # Добавляем игру в подписку
            insert_query = "INSERT INTO gamesinplans (plan_id, game_id) VALUES (%s, %s)"
            if self.db_manager.execute_update(insert_query, (self.plan_id, game_id)):
                QMessageBox.information(self, "Успех", "Игра добавлена в подписку.")
                self.accept()
                self.close() # После успешного добавления закрываем форму
        else:
            QMessageBox.warning(self, "Ошибка", f"Игра с названием '{game_title}' не найдена в базе данных.")