import sys
import csv
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QDialog, QFileDialog,
                             QHBoxLayout, QStackedWidget, QMessageBox, QTableWidget, QApplication,
                             QTableWidgetItem, QAbstractItemView, QDateEdit, QGroupBox, QComboBox, QLineEdit, QFormLayout)
from PyQt5.QtCore import QDate, Qt
from db_manager import DatabaseManager


class AdminPanelForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Панель администратора')
        self.setMinimumSize(800, 600)

        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        # Создаем вкладки
        self.reports_button = QPushButton('Отчёты')
        self.sales_button = QPushButton('Проданные подписки')
        self.reports_button.clicked.connect(self.show_reports_page)
        self.sales_button.clicked.connect(self.show_sales_page)

        tabs_layout = QHBoxLayout()
        tabs_layout.addWidget(self.reports_button)
        tabs_layout.addWidget(self.sales_button)

        # Создаем QStackedWidget для переключения между страницами
        self.stacked_widget = QStackedWidget()

        # Создаем страницы
        self.create_reports_page()
        self.create_sales_page()

        # Добавляем страницы в stacked_widget
        self.stacked_widget.addWidget(self.reports_page)
        self.stacked_widget.addWidget(self.sales_page)

        # Кнопки навигации
        self.catalog_button = QPushButton('Каталог игр')
        self.catalog_button.clicked.connect(self.main_window.show_game_catalog_form)
        self.subscriptions_button = QPushButton('Редактирование подписок')
        self.subscriptions_button.clicked.connect(self.main_window.show_subscription_catalog_form)
        self.admin_button = QPushButton('Панель администратора')
        self.admin_button.clicked.connect(self.main_window.show_admin_panel_form)
        self.exit_button = QPushButton('Выход')
        self.exit_button.clicked.connect(self.main_window.close)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.catalog_button)
        nav_layout.addWidget(self.subscriptions_button)
        nav_layout.addWidget(self.admin_button)
        nav_layout.addWidget(self.exit_button)

        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(tabs_layout)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(nav_layout)

        # Показываем страницу отчетов при запуске
        self.show_reports_page()

    def show_reports_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_sales_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def create_reports_page(self):
        # Создание страницы с отчетами
        self.reports_page = QWidget()
        reports_layout = QVBoxLayout()

        # Виджеты для выбора периода
        period_group = QGroupBox("Выбор периода")
        period_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        period_layout.addWidget(QLabel("Начало периода:"))
        period_layout.addWidget(self.start_date_edit)
        period_layout.addWidget(QLabel("Конец периода:"))
        period_layout.addWidget(self.end_date_edit)
        period_group.setLayout(period_layout)

        # Таблица отчётов
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(['ID', 'Дата', 'ID плана', 'Доход', 'Расход'])
        self.report_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Кнопки
        self.generate_report_button = QPushButton('Сформировать отчёт')
        self.generate_report_button.clicked.connect(self.generate_report)
        self.export_report_button = QPushButton('Экспорт в CSV')
        self.export_report_button.clicked.connect(self.export_report_to_csv)
        self.edit_report_button = QPushButton('Изменить отчёт')
        self.edit_report_button.clicked.connect(self.edit_report)
        self.delete_report_button = QPushButton('Удалить отчёт')
        self.delete_report_button.clicked.connect(self.delete_report)

        # Размещение виджетов на странице отчётов
        reports_buttons_layout = QHBoxLayout()
        reports_buttons_layout.addWidget(self.generate_report_button)
        reports_buttons_layout.addWidget(self.export_report_button)
        reports_buttons_layout.addWidget(self.edit_report_button)
        reports_buttons_layout.addWidget(self.delete_report_button)

        reports_layout.addWidget(period_group)
        reports_layout.addWidget(self.report_table)
        reports_layout.addLayout(reports_buttons_layout)
        self.reports_page.setLayout(reports_layout)

        # Загрузка данных в таблицу отчётов
        self.load_reports_data()

    def create_sales_page(self):
        # Создание страницы с проданными подписками
        self.sales_page = QWidget()
        sales_layout = QVBoxLayout()

        # Таблица проданных подписок
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(['Дата', 'ID подписки', 'Метод оплаты', 'ID платежа', ''])
        self.sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Кнопка "Добавить продажу"
        self.add_sale_button = QPushButton('Добавить продажу')
        self.add_sale_button.clicked.connect(self.add_sale)

        # Размещение виджетов на странице продаж
        sales_layout.addWidget(self.sales_table)
        sales_layout.addWidget(self.add_sale_button)
        self.sales_page.setLayout(sales_layout)

        # Загрузка данных в таблицу продаж
        self.load_sales_data()

    def load_reports_data(self):
        # Загрузка данных в таблицу отчётов
        query = "SELECT report_id, date, plan_id, total_revenue, total_expenses FROM reports"
        reports_data = self.db_manager.execute_query(query)

        if reports_data:
            self.report_table.setRowCount(len(reports_data))
            for row, data in enumerate(reports_data):
                for col, value in enumerate(data):
                    self.report_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.report_table.resizeColumnsToContents()
        else:
            self.report_table.setRowCount(0)

    def generate_report(self):
        # Генерация отчёта за выбранный период
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        query = f"SELECT * FROM reports WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        report_data = self.db_manager.execute_query(query)

        if report_data:
            self.report_table.setRowCount(len(report_data))
            for row, data in enumerate(report_data):
                for col, value in enumerate(data):
                    self.report_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.report_table.resizeColumnsToContents()
        else:
            self.report_table.setRowCount(0)
            QMessageBox.information(self, "Отчёт", "Нет данных для отображения.")

    def add_report(self):
        # Добавление нового отчёта
        add_report_form = AddEditReportForm(self)
        if add_report_form.exec_() == QDialog.Accepted:
            self.load_reports_data()

    def edit_report(self):
        # Редактирование выбранного отчёта
        current_row = self.report_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите отчёт для редактирования.")
            return

        report_data = {
            'report_id': self.report_table.item(current_row, 0).text(),
            'date': self.report_table.item(current_row, 1).text(),
            'plan_id': self.report_table.item(current_row, 2).text(),
            'total_revenue': self.report_table.item(current_row, 3).text(),
            'total_expenses': self.report_table.item(current_row, 4).text()
        }

        edit_report_form = AddEditReportForm(self, **report_data)
        if edit_report_form.exec_() == QDialog.Accepted:
            self.load_reports_data()

    def delete_report(self, row=None):
        # Удаление выбранного отчёта
        current_row = self.report_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите отчёт для удаления.")
            return

        report_id = self.report_table.item(current_row, 0).text()
        reply = QMessageBox.question(self, 'Удаление отчёта', f'Вы уверены, что хотите удалить отчёт с ID {report_id}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            query = "DELETE FROM reports WHERE report_id = %s"
            if self.db_manager.execute_update(query, (report_id,)):
                self.report_table.removeRow(current_row)
                QMessageBox.information(self, "Успех", f"Отчёт с ID {report_id} успешно удален.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить отчёт с ID {report_id}.")

    def export_report_to_csv(self):
        # Экспорт отчёта в CSV файл
        file_name, _ = QFileDialog.getSaveFileName(self, 'Сохранить отчёт', '', 'CSV Files (*.csv)')
        if file_name:
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                headers = [self.report_table.horizontalHeaderItem(i).text() for i in
                           range(self.report_table.columnCount())]
                writer.writerow(headers)
                for row in range(self.report_table.rowCount()):
                    row_data = [self.report_table.item(row, col).text() for col in
                                range(self.report_table.columnCount())]
                    writer.writerow(row_data)
            QMessageBox.information(self, "Экспорт", "Отчёт успешно экспортирован в CSV файл.")

    def load_sales_data(self):
        # Загрузка данных в таблицу проданных подписок
        query = "SELECT payment_date, plan_id, payment_method, payment_id FROM payments"
        sales_data = self.db_manager.execute_query(query)

        if sales_data:
            self.sales_table.setRowCount(len(sales_data))
            for row, data in enumerate(sales_data):
                for col, value in enumerate(data):
                    self.sales_table.setItem(row, col, QTableWidgetItem(str(value)))

                # Добавляем кнопки "Изменить" и "Удалить"
                edit_button = QPushButton("Изменить")
                delete_button = QPushButton("Удалить")
                edit_button.clicked.connect(lambda _, r=row: self.edit_sale(r))
                delete_button.clicked.connect(lambda _, r=row: self.delete_sale(r))

                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.addWidget(edit_button)
                button_layout.addWidget(delete_button)
                button_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы
                button_layout.setAlignment(Qt.AlignCenter)  # Центрируем кнопки
                self.sales_table.setCellWidget(row, 4, button_widget)

            self.sales_table.resizeColumnsToContents()
        else:
            self.sales_table.setRowCount(0)

    def add_sale(self):
        add_sale_form = AddSaleForm(self)
        if add_sale_form.exec_() == QDialog.Accepted:
            sale_data = add_sale_form.get_sale_data()
            print(f"add_sale: sale_data = {sale_data}")

            # Добавляем данные в базу данных payments
            insert_query = "INSERT INTO payments (payment_date, plan_id, payment_method) VALUES (%s, %s, %s)"
            plan_id = self.get_plan_id_by_name(sale_data[1])
            payment_method = sale_data[3]

            if plan_id is not None:
                cursor = self.db_manager.cursor()
                cursor.execute(insert_query, (sale_data[0], plan_id, payment_method))
                payment_id = cursor.lastrowid
                cursor.close()

                if payment_id:
                    # Добавление записи в базу данных reports
                    report_insert_query = """
                        INSERT INTO reports (date, plan_id, total_revenue, total_expenses)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE total_revenue = total_revenue + VALUES(total_revenue);
                    """
                    revenue = float(sale_data[2].split()[0]) if sale_data[2] is not None and sale_data[2].split() else 0.0
                    report_params = (sale_data[0], plan_id, revenue, 0)

                    self.db_manager.execute_update(report_insert_query, report_params)

                    # Обновляем таблицы на форме после успешного добавления
                    self.load_sales_data()
                    self.load_reports_data()
                    QMessageBox.information(self, "Успех", "Продажа успешно добавлена.")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить продажу в базу данных.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти ID подписки.")

    def edit_sale(self, row):
        # Редактирование выбранной продажи
        payment_id = self.sales_table.item(row, 3).text()
        current_date = self.sales_table.item(row, 0).text()
        current_plan_id = self.sales_table.item(row, 1).text()
        current_payment_method = self.sales_table.item(row, 2).text()

        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle('Редактировать продажу')

        date_label = QLabel('Дата продажи:')
        date_edit = QDateEdit(QDate.fromString(current_date, "yyyy-MM-dd"))
        date_edit.setCalendarPopup(True)

        plan_id_label = QLabel('ID подписки:')
        plan_id_combo = QComboBox()
        plan_list = self.db_manager.execute_query("SELECT plan_id, plan_name FROM plans")
        for plan_id, plan_name in plan_list:
            plan_id_combo.addItem(f"{plan_id} - {plan_name}", plan_id)

        index = plan_id_combo.findData(int(current_plan_id))
        if index != -1:
            plan_id_combo.setCurrentIndex(index)

        payment_method_label = QLabel('Метод оплаты:')
        payment_method_input = QLineEdit(current_payment_method)

        save_button = QPushButton('Сохранить')
        cancel_button = QPushButton('Отмена')

        layout = QVBoxLayout()
        layout.addWidget(date_label)
        layout.addWidget(date_edit)
        layout.addWidget(plan_id_label)
        layout.addWidget(plan_id_combo)
        layout.addWidget(payment_method_label)
        layout.addWidget(payment_method_input)
        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        edit_dialog.setLayout(layout)

        def save_changes():
            new_date = date_edit.date().toString("yyyy-MM-dd")
            new_plan_id = plan_id_combo.currentData()
            new_payment_method = payment_method_input.text()

            if (new_date == current_date and
                    str(new_plan_id) == current_plan_id and
                    new_payment_method == current_payment_method):
                QMessageBox.information(self, "Информация", "Данные не были изменены.")
                edit_dialog.close()
                return

            update_query = """
                UPDATE payments
                SET payment_date = %s, plan_id = %s, payment_method = %s
                WHERE payment_id = %s
            """
            if self.db_manager.execute_update(update_query, (new_date, new_plan_id, new_payment_method, payment_id)):
                self.sales_table.item(row, 0).setText(new_date)
                self.sales_table.item(row, 1).setText(str(new_plan_id))
                self.sales_table.item(row, 2).setText(new_payment_method)
                QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
                edit_dialog.close()
                self.load_sales_data()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные.")

        save_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(edit_dialog.reject)

        edit_dialog.exec_()

    def delete_sale(self, row):
        # Удаление выбранной продажи
        payment_id = self.sales_table.item(row, 3).text()
        reply = QMessageBox.question(self, 'Удаление продажи',
                                     f'Вы уверены, что хотите удалить продажу с ID {payment_id}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            query = "DELETE FROM payments WHERE payment_id = %s"
            if self.db_manager.execute_update(query, (payment_id,)):
                self.sales_table.removeRow(row)
                QMessageBox.information(self, "Успех", f"Продажа с ID {payment_id} успешно удалена.")
                self.load_sales_data()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить продажу с ID {payment_id}.")

    def get_plan_id_by_name(self, plan_name):
        query = "SELECT plan_id FROM plans WHERE plan_name = %s"
        result = self.db_manager.execute_query(query, (plan_name,), fetch_all=False)
        if result:
            return result[0]
        else:
            return None

class AddSaleForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить продажу')

        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        self.date_label = QLabel('Дата продажи:')
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        self.subscription_label = QLabel('Подписка:')
        self.subscription_combo = QComboBox()
        self.load_subscriptions()

        self.buyer_label = QLabel('Покупатель (или метод оплаты):')
        self.buyer_input = QLineEdit()

        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_edit)
        layout.addWidget(self.subscription_label)
        layout.addWidget(self.subscription_combo)
        layout.addWidget(self.buyer_label)
        layout.addWidget(self.buyer_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Добавляем словарь с ценами
        self.subscription_prices = {}
        self.load_subscription_prices()
        self.price = None  # Атрибут для хранения цены

        # Обработчик изменения QComboBox
        self.subscription_combo.currentIndexChanged.connect(self.update_price)

    def load_subscriptions(self):
        # Загрузка подписок из БД
        query = "SELECT plan_name FROM plans"
        subscriptions = self.db_manager.execute_query(query)
        if subscriptions:
            for sub in subscriptions:
                self.subscription_combo.addItem(sub[0])

    def load_subscription_prices(self):
        # Загрузка цен из БД
        query = "SELECT plan_name, price FROM plans"
        prices = self.db_manager.execute_query(query)
        if prices:
            for plan_name, price in prices:
                self.subscription_prices[plan_name] = str(price) + " руб."

    def update_price(self):
        # Получаем цену из словаря по выбранной подписке
        self.price = self.subscription_prices.get(self.subscription_combo.currentText())

    def get_sale_data(self):
        return (
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.subscription_combo.currentText(),
            self.price,  # Добавляем цену в возвращаемые данные
            self.buyer_input.text()
        )

class AddEditReportForm(QDialog):
    def __init__(self, parent=None, report_id=None, report_date=None, plan_id=None, total_revenue=None, total_expenses=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить/изменить отчёт')
        self.db_manager = parent.db_manager  # Используем db_manager из родительского окна
        self.report_id = report_id

        # Поля формы
        self.date_label = QLabel('Дата:')
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        self.plan_id_label = QLabel('ID плана:')
        self.plan_id_combo = QComboBox()
        self.load_plan_ids()

        self.revenue_label = QLabel('Доход:')
        self.revenue_edit = QLineEdit()

        self.expenses_label = QLabel('Расход:')
        self.expenses_edit = QLineEdit()

        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.save_report)
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.clicked.connect(self.reject)

        # Размещение элементов на форме
        layout = QFormLayout()
        layout.addRow(self.date_label, self.date_edit)
        layout.addRow(self.plan_id_label, self.plan_id_combo)
        layout.addRow(self.revenue_label, self.revenue_edit)
        layout.addRow(self.expenses_label, self.expenses_edit)
        layout.addRow(self.save_button, self.cancel_button)
        self.setLayout(layout)

        # Заполняем поля, если это редактирование
        if report_id:
            self.date_edit.setDate(QDate.fromString(report_date, "yyyy-MM-dd"))
            index = self.plan_id_combo.findText(plan_id)
            if index != -1:
                self.plan_id_combo.setCurrentIndex(index)
            self.revenue_edit.setText(total_revenue)
            self.expenses_edit.setText(total_expenses)

    def load_plan_ids(self):
        # Загрузка ID планов в QComboBox
        query = "SELECT plan_id, plan_name FROM plans"
        plan_list = self.db_manager.execute_query(query)
        for plan_id, plan_name in plan_list:
            self.plan_id_combo.addItem(f"{plan_id} - {plan_name}", plan_id)

    def save_report(self):
        # Получаем данные из полей
        report_date = self.date_edit.date().toString("yyyy-MM-dd")
        plan_id = self.plan_id_combo.currentData()
        total_revenue = self.revenue_edit.text()
        total_expenses = self.expenses_edit.text()

        # Проверяем, что поля заполнены
        if not all([report_date, plan_id, total_revenue, total_expenses]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля!')
            return

        # Проверяем, что plan_id существует
        if not self.parent().get_plan_id_by_name(plan_id):
            QMessageBox.warning(self, "Ошибка", f"Плана с ID {plan_id} не существует.")
            return

        # Добавляем или обновляем запись в БД
        if self.report_id:
            # Редактирование существующего отчёта
            query = """
                UPDATE reports
                SET date = %s, plan_id = %s, total_revenue = %s, total_expenses = %s
                WHERE report_id = %s
            """
            params = (report_date, plan_id, total_revenue, total_expenses, self.report_id)
        else:
            # Добавление нового отчёта
            query = """
                INSERT INTO reports (date, plan_id, total_revenue, total_expenses)
                VALUES (%s, %s, %s, %s)
            """
            params = (report_date, plan_id, total_revenue, total_expenses)

        cursor = self.db_manager.cursor()
        try:
            cursor.execute(query, params)
            if not self.report_id:
                self.report_id = cursor.lastrowid
            self.db_manager.commit()
            QMessageBox.information(self, "Успех", "Отчёт сохранен.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить отчёт: {e}")
        finally:
            cursor.close()

        # Проверяем, что поля заполнены
        if not all([report_date, plan_id, total_revenue, total_expenses]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля!')
            return

        # Проверяем, что plan_id существует
        if not self.parent().get_plan_id_by_name(plan_id):
            QMessageBox.warning(self, "Ошибка", f"Плана с ID {plan_id} не существует.")
            return

        # Добавляем или обновляем запись в БД
        if self.report_id:
            # Редактирование существующего отчёта
            query = """
                UPDATE reports
                SET date = %s, plan_id = %s, total_revenue = %s, total_expenses = %s
                WHERE report_id = %s
            """
            params = (report_date, plan_id, total_revenue, total_expenses, self.report_id)
        else:
            # Добавление нового отчёта
            query = """
                INSERT INTO reports (date, plan_id, total_revenue, total_expenses)
                VALUES (%s, %s, %s, %s)
            """
            params = (report_date, plan_id, total_revenue, total_expenses)

        if self.db_manager.execute_update(query, params) >= 0:
            QMessageBox.information(self, "Успех", "Отчёт сохранен.")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить отчёт.")