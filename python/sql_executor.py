import mysql.connector
from mysql.connector import Error

class SQLExecutor():

    def __init__(self):
        try:
            with open("python/connection_info.txt", "r") as f:
                lines = [s.strip() for s in f.readlines()]
                host_arg, user_arg, password_arg, database_arg = lines[0], lines[1], lines[2], lines[3]
            
            self.connection = mysql.connector.connect(
                host=host_arg,
                user=user_arg,
                password=password_arg,
                database=database_arg
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
            else:
                print("Could not connect")

        except Error as e:
            print(f"Error while connecting: {e}")

    def is_connected(self) -> bool:
        return self.connection.is_connected()

    def close(self):
        if 'connection' in locals() and self.connection.is_connected():
            self.connection.close()
            self.cursor.close()

    def query(self, query):
        if not self.connection.is_connected():
            return []
        
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def select(self, target, source):
        if not self.connection.is_connected():
            return []
        
        query = f"SELECT {target} FROM {source};"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

