from mysql.connector.connection import MySQLConnection
import mysql.connector
from mysql.connector import errorcode

class DatabaseManager(MySQLConnection):
    def __init__(self, host, user, password, database):
        self._consume_results = None
        self._unread_result = False
        self._host = host
        self._user = user
        self._password = password
        self._database = database

        # Инициализируем подключение к базе данных в конструкторе
        self.connect_to_db()

    def connect_to_db(self):
        try:
            # Инициализация MySQLConnection с использованием аргументов
            super().__init__(host=self._host, user=self._user, password=self._password, database=self._database)
            if not self.is_connected():
                self.reconnect(attempts=3, delay=5)

            if not self.is_connected():
                raise mysql.connector.Error(msg="Не удалось подключиться к базе данных после нескольких попыток.", errno=errorcode.CR_CONNECTION_ERROR)

            # Проверяем и создаем базу данных, если она не существует
            self.create_database_if_not_exists(self._database)

            # Создаем таблицы
            self.create_tables()

        except mysql.connector.Error as err:
            print(f"Ошибка при подключении к базе данных: {err}")
            exit(1)

        except mysql.connector.Error as err:
            print(f"Ошибка при подключении к базе данных: {err}")
            exit(1)

    def create_database_if_not_exists(self, db_name):
        # Проверяем, существует ли база данных
        if not self.check_database_exists(db_name):
            self.create_database(db_name)

    def create_database(self, db_name):
        cursor = self.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
            print(f"База данных '{db_name}' успешно создана.")
        except mysql.connector.Error as err:
            print(f"Не удалось создать базу данных: {err}")
            exit(1)
        finally:
            cursor.close()

    def check_database_exists(self, db_name):
        cursor = self.cursor()
        try:
            cursor.execute(f"USE {db_name}")
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                return False
            else:
                print(f"Ошибка при проверке существования базы данных: {err}")
                exit(1)
        finally:
            cursor.close()

    def create_tables(self):
        cursor = self.cursor()

        table_creation_queries = [
            """
            CREATE TABLE IF NOT EXISTS Games (
                game_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) UNIQUE NOT NULL,
                genre VARCHAR(255),
                developer VARCHAR(255),
                publisher VARCHAR(255),
                release_date DATE,
                description TEXT,
                game_key VARCHAR(255),
                image_path VARCHAR(255)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Plans (
                plan_id INT AUTO_INCREMENT PRIMARY KEY,
                plan_name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                duration_up_to INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS GamesInPlans (
                plan_id INT,
                game_id INT,
                PRIMARY KEY (plan_id, game_id),
                FOREIGN KEY (plan_id) REFERENCES Plans(plan_id),
                FOREIGN KEY (game_id) REFERENCES Games(game_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Payments (
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                payment_date DATE NOT NULL,
                plan_id INT NOT NULL,
                payment_method VARCHAR(255),
                FOREIGN KEY (plan_id) REFERENCES Plans(plan_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Reports (
                report_id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE UNIQUE NOT NULL,
                plan_id INT NOT NULL,
                total_revenue DECIMAL(10, 2),
                total_expenses DECIMAL(10, 2),
                FOREIGN KEY (plan_id) REFERENCES Plans(plan_id)
            )
            """
        ]

        for query in table_creation_queries:
            try:
                cursor.execute(query)
                print(f"Таблица успешно создана.")
            except mysql.connector.Error as err:
                print(f"Ошибка при создании таблицы: {err}")

        cursor.close()

    def execute_query(self, query, params=None, fetch_all=True):
        cursor = None
        try:
            cursor = self.cursor()
            cursor.execute(query, params or ())

            if fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()

            self.commit()
            return result
        except mysql.connector.Error as err:
            print(f"Ошибка при выполнении запроса: {err}")
            print(f"Запрос: {query}")  # Добавлено для отладки
            print(f"Параметры: {params}")  # Добавлено для отладки
            return None
        finally:
            if cursor:
                cursor.close()

    def execute_update(self, query, params=None):
        cursor = None
        try:
            cursor = self.cursor()
            cursor.execute(query, params or ())

            self.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Ошибка при выполнении запроса: {err}")
            print(f"Запрос: {query}")  # Добавлено для отладки
            print(f"Параметры: {params}")  # Добавлено для отладки
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_connection_params(self):
        return {
            'host': self._host,
            'user': self._user,
            'password': self._password,
            'database': self.database
        }