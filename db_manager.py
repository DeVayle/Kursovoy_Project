from mysql.connector.connection import MySQLConnection
import mysql.connector

class DatabaseManager(MySQLConnection):
    def __init__(self, host, user, password, database):
        super().__init__(host=host, user=user, password=password, database=database)

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