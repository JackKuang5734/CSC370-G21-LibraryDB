from pkg_resources import SOURCE_DIST
from sympy import solve_poly_inequality
from menus import Menu
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget
from model import Model
from sql_executor import SQLResult
from table import Table


class MainView(QWidget):
    def __init__(self, model : Model):
        super().__init__()

        self.model : Model = model

        self.setLayout(QVBoxLayout())

        self.table : Table = Table()

        self.main_menu = Menu()

        self.main_menu.add_button("Users", self.display_users)
        self.main_menu.add_button("Holds", self.display_holds)
        self.main_menu.add_button("Loans", self.display_loans)
        self.main_menu.add_button("Items", self.display_items)
        self.main_menu.add_button("TEMP", self.display_location_items)
        self.main_menu.add_button("Item Types", self.display_item_types)
        self.main_menu.add_button("Locations", self.display_locations)
        self.main_menu.add_button("Genres", self.display_genres)
        
        self.layout().addWidget(self.main_menu)
        self.layout().addWidget(self.table)

    
    def display_users(self):
        self.display_data(sql_result=self.model.get_users())

    def display_holds(self):
        self.display_data(sql_result=self.model.get_holds())
    
    def display_loans(self):
        self.display_data(sql_result=self.model.get_loans())
    
    def display_items(self):
        self.display_data(sql_result=self.model.get_items(location_id=None))
    
    def display_location_items(self):
        self.display_data(sql_result=self.model.get_items(location_id=2))
    
    def display_item_types(self):
        self.display_data(sql_result=self.model.get_item_types())
    
    def display_locations(self):
        self.display_data(sql_result=self.model.get_locations())

    def display_genres(self):
        self.display_data(sql_result=self.model.get_genres())
    
    def display_data(self, header=None, rows=None, sql_result : SQLResult|None = None):
        if sql_result is not None:
            header = sql_result.header
            rows = sql_result.rows
        if header is not None and rows is not None:
            self.table.display(header, rows)
        else:
            self.table.clear()
    

        # Close the sql connection when the window is closed
    def closeEvent(self, event):
        print("Closing...")
        self.model.close()
        event.accept()
