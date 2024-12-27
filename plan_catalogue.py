from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, \
    QDialog, QAbstractItemView
from db_manager import DatabaseManager
from plan_redactor import EditSubscriptionForm

class SubscriptionCatalogForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Каталог подписок')
        self.setMinimumSize(800, 600)

        # Кнопки навигации
        self.catalog_button = QPushButton('Каталог игр')
        self.catalog_button.clicked.connect(self.open_game_catalog_form)
        self.subscriptions_button = QPushButton('Редактирование подписок')
        self.subscriptions_button.clicked.connect(self.open_subscription_catalog_form)
        self.admin_button = QPushButton('Панель администратора')
        self.admin_button.clicked.connect(self.open_admin_panel_form)
        self.exit_button = QPushButton('Выход')
        self.exit_button.clicked.connect(self.close_form)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.catalog_button)
        nav_layout.addWidget(self.subscriptions_button)
        nav_layout.addWidget(self.admin_button)
        nav_layout.addWidget(self.exit_button)

        # Добавить подписку
        self.add_subscription_button = QPushButton("Добавить подписку")
        self.add_subscription_button.clicked.connect(self.add_subscription)

        # Таблица подписок
        self.subscription_table = QTableWidget()
        self.subscription_table.setColumnCount(6)
        self.subscription_table.setHorizontalHeaderLabels(['ID', 'Название плана', 'Описание', 'Цена', 'Длительность', ''])
        self.subscription_table.setRowCount(0)
        self.subscription_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Таблица игр в подписке
        self.games_in_subscription_table = QTableWidget()
        self.games_in_subscription_table.setColumnCount(6)
        self.games_in_subscription_table.setHorizontalHeaderLabels(
            ['Название', 'Жанр', 'Разработчик', 'Издатель', 'Год выхода', ''])
        self.games_in_subscription_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Размещение таблиц в горизонтальном layout
        tables_layout = QHBoxLayout()
        tables_layout.addWidget(self.subscription_table)
        tables_layout.addWidget(self.games_in_subscription_table)

        # Инициализация DatabaseManager
        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        # Загружаем данные из базы данных
        self.load_plans_from_db()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.add_subscription_button)
        main_layout.addLayout(tables_layout)
        main_layout.addLayout(nav_layout)

        # Подключаем обработчик клика по строке в таблице подписок
        self.subscription_table.cellClicked.connect(self.show_games_in_subscription)

    def add_subscription(self):
        # Открытие формы редактирования подписки
        self.edit_subscription_form = EditSubscriptionForm(self)
        if self.edit_subscription_form.exec_() == QDialog.Accepted:
            self.load_plans_from_db()  # Перезагружаем данные после добавления

    def load_plans_from_db(self):
        query = "SELECT plan_id, plan_name, description, price, duration_up_to FROM plans"
        plans = self.db_manager.execute_query(query)

        if plans is not None:
            self.subscription_table.setRowCount(len(plans))
            for row, plan in enumerate(plans):
                self.subscription_table.setItem(row, 0, QTableWidgetItem(str(plan[0])))
                self.subscription_table.setItem(row, 1, QTableWidgetItem(plan[1]))
                self.subscription_table.setItem(row, 2, QTableWidgetItem(plan[2]))
                self.subscription_table.setItem(row, 3, QTableWidgetItem(str(plan[3])))
                self.subscription_table.setItem(row, 4, QTableWidgetItem(str(plan[4])))

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
                self.subscription_table.setCellWidget(row, 5, cell_widget)

                edit_button.clicked.connect(lambda _, row=row: self.edit_subscription(row))
                delete_button.clicked.connect(lambda _, row=row: self.delete_subscription(row))

            self.subscription_table.resizeColumnsToContents()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные из БД.")

    def delete_subscription(self, row):
        plan_id = self.subscription_table.item(row, 0).text()
        plan_name = self.subscription_table.item(row, 1).text()

        # Запрашиваем подтверждение удаления
        reply = QMessageBox.question(self, 'Удаление подписки', f'Вы уверены, что хотите удалить подписку "{plan_name}"?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Сначала удаляем связанные записи из таблицы payments
            delete_payments_query = "DELETE FROM payments WHERE plan_id = %s"
            self.db_manager.execute_update(delete_payments_query, (plan_id,))

            # Проверяем, есть ли игры в подписке
            check_games_query = "SELECT 1 FROM gamesinplans WHERE plan_id = %s"
            games_exist = self.db_manager.execute_query(check_games_query, (plan_id,), fetch_all=False)

            # Если игры есть, удаляем их
            if games_exist:
                delete_games_query = "DELETE FROM gamesinplans WHERE plan_id = %s"
                self.db_manager.execute_update(delete_games_query, (plan_id,))

            # Теперь удаляем саму подписку
            delete_plan_query = "DELETE FROM plans WHERE plan_id = %s"
            if self.db_manager.execute_update(delete_plan_query, (plan_id,)):
                # Удаляем строку из таблицы
                self.subscription_table.removeRow(row)
                self.games_in_subscription_table.clearContents()
                self.games_in_subscription_table.setRowCount(0)
                QMessageBox.information(self, "Успех", f"Подписка '{plan_name}' успешно удалена.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить подписку '{plan_name}'.")

    def edit_subscription(self, row):
        # Получение данных подписки для редактирования
        plan_data = {
            'plan_id': self.subscription_table.item(row, 0).text(),
            'plan_name': self.subscription_table.item(row, 1).text(),
            'description': self.subscription_table.item(row, 2).text(),
            'price': self.subscription_table.item(row, 3).text(),
            'duration_up_to': self.subscription_table.item(row, 4).text()
        }
        # Открытие формы редактирования подписки
        self.edit_subscription_form = EditSubscriptionForm(self, plan_data)
        self.edit_subscription_form.add_game_button.setEnabled(True) # Добавлено
        self.edit_subscription_form.remove_game_button.setEnabled(True) # Добавлено
        if self.edit_subscription_form.exec_() == QDialog.Accepted:
            self.load_plans_from_db()  # Перезагружаем данные после добавления
            self.show_games_in_subscription(row, 0)

    def show_games_in_subscription(self, row, column):
        if row >= 0:
            selected_plan_id = self.subscription_table.item(row, 0).text()

            # Запрос для получения игр в выбранной подписке
            query = """
                SELECT g.title, g.genre, g.developer, g.publisher, g.release_date
                FROM games g
                JOIN gamesinplans gp ON g.game_id = gp.game_id
                WHERE gp.plan_id = %s
            """
            games_in_plan = self.db_manager.execute_query(query, (selected_plan_id,))

            if games_in_plan is not None:
                self.games_in_subscription_table.setRowCount(len(games_in_plan))
                for row_index, game in enumerate(games_in_plan):
                    self.games_in_subscription_table.setItem(row_index, 0, QTableWidgetItem(game[0]))
                    self.games_in_subscription_table.setItem(row_index, 1, QTableWidgetItem(game[1]))
                    self.games_in_subscription_table.setItem(row_index, 2, QTableWidgetItem(game[2]))
                    self.games_in_subscription_table.setItem(row_index, 3, QTableWidgetItem(game[3]))
                    self.games_in_subscription_table.setItem(row_index, 4, QTableWidgetItem(str(game[4])))

                self.games_in_subscription_table.resizeColumnsToContents()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные из БД.")
        else:
            self.games_in_subscription_table.setRowCount(0)
            self.games_in_subscription_table.clearContents()

    def open_game_catalog_form(self):
        self.main_window.show_game_catalog_form()

    def open_admin_panel_form(self):
        self.main_window.show_admin_panel_form()

    def close_form(self):
        self.main_window.close()

    def open_subscription_catalog_form(self):
        # Переход к форме каталога подписок
        self.main_window.show_subscription_catalog_form()