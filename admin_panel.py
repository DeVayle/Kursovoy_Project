import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QDialog,
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

        reports_layout.addWidget(period_group)
        reports_layout.addWidget(self.report_table)
        reports_layout.addWidget(self.generate_report_button)
        self.reports_page.setLayout(reports_layout)

        # Страница "Проданные подписки"
        self.sales_page = QWidget()
        sales_layout = QVBoxLayout()

        # Таблица проданных подписок
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels(['Дата', 'ID подписки', 'Метод оплаты', 'ID платежа'])
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
            # Здесь нужно получить plan_id по названию подписки
            plan_id = self.get_plan_id_by_name(sale_data[1])
            payment_method = sale_data[3]  # 'Покупатель' используется как метод платежа, возможно, стоит пересмотреть

            if plan_id is not None:
                payment_id = self.db_manager.execute_query(insert_query, (sale_data[0], plan_id, payment_method),
                                                        fetch_all=False)

                if payment_id:
                    # Добавление записи в базу данных reports
                    report_insert_query = """
                        INSERT INTO reports (date, plan_id, total_revenue, total_expenses)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE total_revenue = total_revenue + VALUES(total_revenue);
                    """
                    # sale_data[2] - это цена, предполагает, что все расходы равны 0
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

                # Добавляем кнопку "Удалить" в каждую строку
                delete_button = QPushButton("Удалить")
                self.sales_table.setCellWidget(row, 4, delete_button)
                delete_button.clicked.connect(lambda _, row=row: self.delete_sale(row))

            self.sales_table.resizeColumnsToContents()
        else:
            self.sales_table.setRowCount(0)

    def delete_sale(self, row):
        payment_id = self.sales_table.item(row, 3).text()

        # Запрашиваем подтверждение удаления
        reply = QMessageBox.question(self, 'Удаление продажи', f'Вы уверены, что хотите удалить продажу с ID {payment_id}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Удаляем запись из БД
            query = "DELETE FROM payments WHERE payment_id = %s"
            if self.db_manager.execute_update(query, (payment_id,)):
                # Удаляем строку из таблицы
                self.sales_table.removeRow(row)
                QMessageBox.information(self, "Успех", f"Продажа с ID {payment_id} успешно удалена.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить продажу с ID {payment_id}.")

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