from email import header
import sys
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QScrollArea, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton
from view import MainView
from table import Table
from sql_executor import SQLExecutor

class Model(QWidget):
    def __init__(self):
        super().__init__()

        self.sql = SQLExecutor()
        self.main_view = MainView(self)
        self.display_id = False

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.main_view)


    def display_query(self, header, query):
        rows = self.sql.query(query)
        self.table.display(header, rows)

    def display_users(self):
        sql_result = self.sql.get_users(self.display_id)
        self.main_view.display_data(sql_result=sql_result)
    
    def display_holds(self):
        sql_result = self.sql.get_holds(self.display_id)
        self.main_view.display_data(sql_result=sql_result)
    
    def display_loans(self):
        sql_result = self.sql.get_loans(self.display_id)
        self.main_view.display_data(sql_result=sql_result)

    def display_item_types(self):
        sql_result = self.sql.get_item_types()
        self.main_view.display_data(sql_result=sql_result)

    def display_items(self):
        sql_result = self.sql.get_items()
        self.main_view.display_data(sql_result=sql_result)

    def display_locations(self):
        sql_result = self.sql.get_locations(self.display_id)
        self.main_view.display_data(sql_result=sql_result)

    def display_genre(self):
        sql_result = self.sql.get_genre(self.display_id)
        self.main_view.display_data(sql_result=sql_result)

    # Close the sql connection when the window is closed
    def closeEvent(self, event):
        print("Closing...")
        self.sql.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = Model()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())