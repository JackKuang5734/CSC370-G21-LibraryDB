from menus import Menu
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from sql_executor import SQLResult
from table import Table


class MainView(QWidget):
    def __init__(self, main):
        super().__init__()

        self.main = main

        self.setLayout(QVBoxLayout())

        self.table : Table = Table()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table)

        self.main_menu = Menu()

        self.main_menu.add_button("Users", self.main.display_users)
        self.main_menu.add_button("Holds", self.main.display_holds)
        self.main_menu.add_button("Loans", self.main.display_loans)
        self.main_menu.add_button("Items", self.main.display_items)
        self.main_menu.add_button("Item Types", self.main.display_item_types)
        self.main_menu.add_button("Locations", self.main.display_locations)
        self.main_menu.add_button("Genres", self.main.display_genre)
        
        self.layout().addWidget(self.main_menu)
        self.layout().addWidget(scroll_area)

    
    def display_users(self):
        self.main.display_users()

    def display_holds(self):
        self.main.display_holds()

    def display_loans(self):
        self.main.display_loans()

    def display_data(self, header=None, rows=None, sql_result : SQLResult|None = None):
        if sql_result is not None:
            header = sql_result.header
            rows = sql_result.rows
        if header is not None and rows is not None:
            self.table.display(header, rows)
        else:
            self.table.clear()