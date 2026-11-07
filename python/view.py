import re
from menu import Menu
from PyQt6.QtWidgets import QScrollArea, QStackedWidget, QVBoxLayout, QWidget
from screen import ItemInfomationScreen
from sql_executor import SQLExecutor, SQLResult
from table import Table


class MainView(QWidget):


    GENERAL_DATA = 0
    ITEM_DETAILS = 1

    def __init__(self, sql : SQLExecutor):
        super().__init__()

        self.sql : SQLExecutor = sql

        self.setLayout(QVBoxLayout())

        self.main_menu = Menu()
        self.main_menu.add_button("Users", self.display_users)
        self.main_menu.add_button("Holds", self.display_holds)
        self.main_menu.add_button("Loans", self.display_loans)
        self.main_menu.add_button("Items", self.display_items)
        self.main_menu.add_button("TEMP", self.display_location_items)
        self.main_menu.add_button("Item Types", self.display_item_types)
        self.main_menu.add_button("Locations", self.display_locations)
        self.main_menu.add_button("Genres", self.display_genres)
        
        self.stacked_widget = QStackedWidget()

        self.table : Table = Table()
        self.item_type_screen = ItemInfomationScreen(self)

        self.layout().addWidget(self.main_menu)
        self.layout().addWidget(self.stacked_widget)

        self.stacked_widget.insertWidget(self.__class__.GENERAL_DATA, self.table)
        self.stacked_widget.insertWidget(self.__class__.ITEM_DETAILS, self.item_type_screen)

        self.stacked_widget.setCurrentIndex(self.__class__.GENERAL_DATA)

    
    def display_users(self):
        self.display_general_data(self.sql.get_users())

    def display_holds(self):
        self.display_general_data(self.sql.get_holds())
    
    def display_loans(self):
        self.display_general_data(self.sql.get_loans())
    
    def display_items(self):
        self.display_general_data(self.sql.get_items())
    
    def display_location_items(self):
        result = self.sql.get_items_from_location(2)
        result.link_columns((self.display_item_type,))
        self.display_general_data(result)
    
    def display_item_types(self):
        self.display_general_data(self.sql.get_item_types())
    
    def display_locations(self):
        self.display_general_data(self.sql.get_locations())

    def display_genres(self):
        self.display_general_data(self.sql.get_genres())
    
    def display_item_type(self, id):
        self.item_type_screen.display_item(self.sql.get_item_type_info(str(id)))
        self.stacked_widget.setCurrentIndex(self.__class__.ITEM_DETAILS)

    def display_general_data(self, sql_result : SQLResult|None = None):
        if sql_result is not None:
            self.table.display(sql_result)
        else:
            self.table.clear()
        self.stacked_widget.setCurrentIndex(self.__class__.GENERAL_DATA)
    

        # Close the sql connection when the window is closed
    def closeEvent(self, event):
        print("Closing...")
        self.sql.close()
        event.accept()
