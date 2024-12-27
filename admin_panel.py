import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QDialog, QFormLayout,
                             QHBoxLayout, QStackedWidget, QMessageBox, QTableWidget, QApplication,
                             QTableWidgetItem, QAbstractItemView, QDateEdit, QGroupBox, QComboBox, QLineEdit)
from PyQt5.QtCore import QDate
from db_manager import DatabaseManager

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

class AdminPanelForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Панель администратора')
        self.setMinimumSize(800, 600)

        # Инициализация DatabaseManager
        self.db_manager = DatabaseManager(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="GameSub"
        )

        # Кнопки-вкладки
        self.reports_button = QPushButton('Отчёты')
        self.sales_button = QPushButton('Проданные подписки')
        self.charts_button = QPushButton('Графики')

        tabs_layout = QHBoxLayout()
        tabs_layout.addWidget(self.reports_button)
        tabs_layout.addWidget(self.sales_button)
        tabs_layout.addWidget(self.charts_button)

        # Область содержимого
        self.stacked_widget = QStackedWidget()

        # Страница "Отчёты"
        self.reports_page = QWidget()
        reports_layout = QVBoxLayout()

        # Выбор периода
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

        # Таблица отчёта
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(['ID отчёта', 'Дата', 'ID плана', 'Доход', 'Расход'])
        self.report_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Запрет на редактирование

        # Кнопка "Сформировать отчёт"
        self.generate_report_button = QPushButton('Сформировать отчёт')
        self.generate_report_button.clicked.connect(self.generate_report)

        # Кнопки для добавления, изменения и удаления отчётов
        self.add_report_button = QPushButton('Добавить отчёт')
        self.add_report_button.clicked.connect(self.add_report)
        self.edit_report_button = QPushButton('Изменить отчёт')
        self.edit_report_button.clicked.connect(self.edit_report)
        self.delete_report_button = QPushButton('Удалить отчёт')
        self.delete_report_button.clicked.connect(self.delete_report)

        reports_buttons_layout = QHBoxLayout()
        reports_buttons_layout.addWidget(self.add_report_button)
        reports_buttons_layout.addWidget(self.edit_report_button)
        reports_buttons_layout.addWidget(self.delete_report_button)

        reports_layout.addWidget(period_group)
        reports_layout.addWidget(self.report_table)
        reports_layout.addWidget(self.generate_report_button)
        reports_layout.addLayout(reports_buttons_layout)
        self.reports_page.setLayout(reports_layout)

        reports_layout.addWidget(period_group)
        reports_layout.addWidget(self.report_table)
        reports_layout.addWidget(self.generate_report_button)
        self.reports_page.setLayout(reports_layout)

        # Страница "Проданные подписки"
        self.sales_page = QWidget()
        sales_layout = QVBoxLayout()

        # Таблица проданных подписок
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(['Дата', 'ID подписки', 'Метод оплаты', 'ID платежа', ''])
        self.sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет на редактирование

        # Кнопка "Добавить продажу"
        self.add_sale_button = QPushButton('Добавить продажу')
        self.add_sale_button.clicked.connect(self.add_sale)

        sales_layout.addWidget(self.sales_table)
        sales_layout.addWidget(self.add_sale_button)
        self.sales_page.setLayout(sales_layout)

        # Страница "Графики"
        self.charts_page = QWidget()
        charts_layout = QVBoxLayout()

        # Создаем FigureCanvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)

        self.charts_page.setLayout(charts_layout)

        # Создаем и настраиваем график
        self.setup_chart()

        # Добавляем страницы в QStackedWidget
        self.stacked_widget.addWidget(self.reports_page)
        self.stacked_widget.addWidget(self.sales_page)
        self.stacked_widget.addWidget(self.charts_page)

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

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(tabs_layout)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(nav_layout)

        self.setLayout(main_layout)

        # Логика переключения вкладок
        self.reports_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.sales_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.charts_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        # Загрузка данных в таблицы при старте
        self.load_sales_data()
        self.load_reports_data()

    def close_with_confirmation(self):
        reply = QMessageBox.question(self, 'Подтверждение выхода', 'Вы уверены, что хотите выйти?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    def generate_report(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        # SQL-запрос для выборки данных из reports в указанном диапазоне дат
        query = """
            SELECT report_id, date, plan_id, total_revenue, total_expenses
            FROM reports
            WHERE date BETWEEN %s AND %s
        """
        report_data = self.db_manager.execute_query(query, (start_date, end_date))

        # Обновляем таблицу
        if report_data:
            self.report_table.setRowCount(len(report_data))
            for row, data in enumerate(report_data):
                for col, value in enumerate(data):
                    self.report_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.report_table.resizeColumnsToContents()
        else:
            self.report_table.setRowCount(0)
            QMessageBox.information(self, "Отчет", "Нет данных для отображения.")

    def add_sale(self):
        add_sale_form = AddSaleForm(self)
        if add_sale_form.exec_() == QDialog.Accepted:
            sale_data = add_sale_form.get_sale_data()

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
                    report_params = (sale_data[0], plan_id, sale_data[2].split()[0], 0)
                    self.db_manager.execute_update(report_insert_query, report_params)

                    # Обновляем таблицу на форме
                    self.load_sales_data()
                    self.load_reports_data()  # Обновляем данные в отчётах
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить продажу в базу данных.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти ID подписки.")

    def get_plan_id_by_name(self, plan_name):
        query = "SELECT plan_id FROM plans WHERE plan_name = %s"
        result = self.db_manager.execute_query(query, (plan_name,), fetch_all=False)
        if result:
            return result[0]
        else:
            return None

    def load_sales_data(self):
        # SQL-запрос для выборки данных из payments
        query = "SELECT payment_date, plan_id, payment_method, payment_id FROM payments"
        sales_data = self.db_manager.execute_query(query)

        # Обновляем таблицу
        if sales_data:
            self.sales_table.setRowCount(len(sales_data))
            for row, data in enumerate(sales_data):
                self.sales_table.setItem(row, 0, QTableWidgetItem(str(data[0])))  # Дата
                self.sales_table.setItem(row, 1, QTableWidgetItem(str(data[1])))  # ID подписки
                self.sales_table.setItem(row, 2, QTableWidgetItem(str(data[2])))  # Метод оплаты
                self.sales_table.setItem(row, 3, QTableWidgetItem(str(data[3])))  # ID платежа

                # Добавляем кнопки "Изменить" и "Удалить" в каждую строку
                button_layout = QHBoxLayout()
                edit_button = QPushButton("Изменить")
                delete_button = QPushButton("Удалить")
                edit_button.setMinimumHeight(20)
                delete_button.setMinimumHeight(20)
                button_layout.addWidget(edit_button)
                button_layout.addWidget(delete_button)
                # Центрируем кнопки в ячейке
                cell_widget = QWidget()
                cell_widget.setLayout(button_layout)
                self.sales_table.setCellWidget(row, 4, cell_widget)

                edit_button.clicked.connect(lambda _, row=row: self.edit_sale(row))
                delete_button.clicked.connect(lambda _, row=row: self.delete_sale(row))

            self.sales_table.resizeColumnsToContents()
        else:
            self.sales_table.setRowCount(0)
            # Очищаем таблицу, если нет данных
            self.sales_table.clearContents()

    def edit_sale(self, row):
        # Получаем данные из строки таблицы
        payment_id = self.sales_table.item(row, 3).text()
        current_date = self.sales_table.item(row, 0).text()
        current_plan_id = self.sales_table.item(row, 1).text()
        current_payment_method = self.sales_table.item(row, 2).text()

        # Создаем диалоговое окно для редактирования
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle('Редактировать продажу')

        # Поля для редактирования
        date_label = QLabel('Дата продажи:')
        date_edit = QDateEdit(QDate.fromString(current_date, "yyyy-MM-dd"))
        date_edit.setCalendarPopup(True)

        plan_id_label = QLabel('ID подписки:')
        plan_id_combo = QComboBox()  # Используем QComboBox
        # Заполняем QComboBox списком подписок
        plan_list = self.db_manager.execute_query("SELECT plan_id, plan_name FROM plans")
        for plan_id, plan_name in plan_list:
            plan_id_combo.addItem(f"{plan_id} - {plan_name}", plan_id)

        # Устанавливаем текущее значение в QComboBox
        index = plan_id_combo.findData(int(current_plan_id))
        if index != -1:
            plan_id_combo.setCurrentIndex(index)

        payment_method_label = QLabel('Метод оплаты:')
        payment_method_input = QLineEdit(current_payment_method)

        # Кнопки "Сохранить" и "Отмена"
        save_button = QPushButton('Сохранить')
        cancel_button = QPushButton('Отмена')

        # Размещение элементов в диалоговом окне
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

        # Обработчики кнопок
        def save_changes():
            new_date = date_edit.date().toString("yyyy-MM-dd")
            new_plan_id = plan_id_combo.currentData()  # Получаем данные из QComboBox
            new_payment_method = payment_method_input.text()

            # Проверяем, были ли изменены данные
            if (new_date == current_date and
                    str(new_plan_id) == current_plan_id and
                    new_payment_method == current_payment_method):
                QMessageBox.information(self, "Информация", "Данные не были изменены.")
                edit_dialog.close()
                return

            # Обновляем данные в БД
            update_query = """
                UPDATE payments
                SET payment_date = %s, plan_id = %s, payment_method = %s
                WHERE payment_id = %s
            """
            if self.db_manager.execute_update(update_query, (new_date, new_plan_id, new_payment_method, payment_id)):
                # Обновляем данные в таблице
                self.sales_table.item(row, 0).setText(new_date)
                self.sales_table.item(row, 1).setText(str(new_plan_id))
                self.sales_table.item(row, 2).setText(new_payment_method)
                QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
                edit_dialog.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные.")

        save_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(edit_dialog.reject)

        # Отображаем диалоговое окно
        edit_dialog.exec_()

    def delete_sale(self, row):
        payment_id = self.sales_table.item(row, 3).text()

        # Запрашиваем подтверждение удаления
        reply = QMessageBox.question(self, 'Удаление продажи', f'Вы уверены, что хотите удалить продажу с ID {payment_id}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Удаляем запись из БД
            query = "DELETE FROM payments WHERE payment_id = %s"
            if self.db_manager.execute_update(query, (payment_id,)):
                # Обновляем таблицу
                self.load_sales_data()
                QMessageBox.information(self, "Успех", f"Продажа с ID {payment_id} успешно удалена.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить продажу с ID {payment_id}.")

    def add_report(self):
        add_report_form = AddEditReportForm(self)
        if add_report_form.exec_() == QDialog.Accepted:
            self.load_reports_data()

    def edit_report(self):
        # Получаем индекс выбранной строки
        current_row = self.report_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите отчёт для редактирования.")
            return

        # Получаем данные отчёта из таблицы
        report_id = self.report_table.item(current_row, 0).text()
        report_date = self.report_table.item(current_row, 1).text()
        plan_id = self.report_table.item(current_row, 2).text()
        total_revenue = self.report_table.item(current_row, 3).text()
        total_expenses = self.report_table.item(current_row, 4).text()

        # Создаем форму редактирования и передаем ей данные
        edit_report_form = AddEditReportForm(self, report_id, report_date, plan_id, total_revenue, total_expenses)
        if edit_report_form.exec_() == QDialog.Accepted:
            self.load_reports_data()

    def delete_report(self):
        # Получаем индекс выбранной строки
        current_row = self.report_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите отчёт для удаления.")
            return

        # Получаем ID отчёта
        report_id = self.report_table.item(current_row, 0).text()

        # Запрашиваем подтверждение удаления
        reply = QMessageBox.question(self, 'Удаление отчёта', f'Вы уверены, что хотите удалить отчёт с ID {report_id}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Удаляем запись из БД
            query = "DELETE FROM reports WHERE report_id = %s"
            if self.db_manager.execute_update(query, (report_id,)):
                # Удаляем строку из таблицы
                self.report_table.removeRow(current_row)
                QMessageBox.information(self, "Успех", f"Отчёт с ID {report_id} успешно удален.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить отчёт с ID {report_id}.")

    def load_reports_data(self):
        # SQL-запрос для выборки всех данных из reports
        query = "SELECT report_id, date, plan_id, total_revenue, total_expenses FROM reports"
        reports_data = self.db_manager.execute_query(query)

        # Обновляем таблицу
        if reports_data:
            self.report_table.setRowCount(len(reports_data))
            for row, data in enumerate(reports_data):
                for col, value in enumerate(data):
                    self.report_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.report_table.resizeColumnsToContents()
        else:
            self.report_table.setRowCount(0)

    def setup_chart(self):
        # Получаем данные из таблицы "Проданные подписки"
        sales_data = []
        for row in range(self.sales_table.rowCount()):
            subscription_id = self.sales_table.item(row, 1).text()
            sales_data.append(subscription_id)

        # Группируем данные по подпискам и считаем количество продаж
        subscription_counts = {}
        for subscription in sales_data:
            if subscription in subscription_counts:
                subscription_counts[subscription] += 1
            else:
                subscription_counts[subscription] = 1

        # Сортируем подписки по алфавиту
        sorted_subscriptions = sorted(subscription_counts.keys())
        sorted_counts = [subscription_counts[subscription] for subscription in sorted_subscriptions]

        # Очищаем график
        self.figure.clear()

        # Создаем subplot
        ax = self.figure.add_subplot(111)

        # Строим столбчатую диаграмму
        bars = ax.bar(sorted_subscriptions, sorted_counts)

        # Добавляем легенду
        ax.legend(bars, sorted_subscriptions, loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=3)

        # Настраиваем внешний вид
        ax.set_title("Продажи подписок")
        ax.set_ylabel("Количество")

        # Ограничиваем количество целочисленных меток по оси Y
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Обновляем canvas
        self.canvas.draw()

    def open_catalog_form(self):
        self.main_window.show_game_catalog_form()

    def open_subscriptions_form(self):
        self.main_window.show_subscription_catalog_form()

    def open_admin_panel_form(self):
        self.main_window.show_admin_panel_form()

    def close_form(self):
        self.main_window.close()

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

        if self.db_manager.execute_update(query, params) >= 0:
            QMessageBox.information(self, "Успех", "Отчёт сохранен.")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить отчёт.")