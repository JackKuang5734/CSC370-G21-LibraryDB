import re
from menu import Menu
from PyQt6.QtWidgets import QLabel, QScrollArea, QStackedWidget, QVBoxLayout, QWidget
from screen import ItemInfomationScreen, SearchScreen
from sql_executor import SQLExecutor, SQLResult
from table import Table


class MainView(QWidget):


    GENERAL_DATA = 0
    ITEM_DETAILS = 1
    SEARCH = 2

    def __init__(self, sql : SQLExecutor):
        super().__init__()

        self.sql : SQLExecutor = sql

        self.setLayout(QVBoxLayout())

        self.main_menu = Menu()
        self.main_menu.add_button("Users", self.display_users)
        self.main_menu.add_button("Browse Location Items", self.display_items_at_location)
        self.main_menu.add_button("Most Loaned Items", self.display_most_loaned_items)
        self.main_menu.add_button("Least Loaned Items", self.display_least_loaned_items)
        self.main_menu.add_button("Most Held Items", self.display_most_held_items)
        self.main_menu.add_button("Least Held Items", self.display_least_held_items)
        self.main_menu.add_button("Popular Genres", self.display_popular_genres)

        self.main_menu.add_button("Item Loans", self.display_item_loan_history)
        self.main_menu.add_button("Item Holds", self.display_item_hold_history)
        self.main_menu.add_button("User Loans", self.display_user_loan_history)
        self.main_menu.add_button("User Holds", self.display_user_hold_history)

        # self.main_menu.add_button("User Holds", self.display_user_holds)
        # self.main_menu.add_button("Holds", self.display_holds)
        # self.main_menu.add_button("Loans", self.display_loans)
        # self.main_menu.add_button("Items", self.display_items)
        # self.main_menu.add_button("Item Types", self.display_item_types)
        # self.main_menu.add_button("Locations", self.display_locations)
        # self.main_menu.add_button("Genres", self.display_genres)
        
        self.stacked_widget = QStackedWidget()

        self.table : Table = Table()
        self.item_type_screen = ItemInfomationScreen(self)
        self.search_screen : SearchScreen = SearchScreen(self)

        self.layout().addWidget(self.main_menu)
        self.layout().addWidget(self.stacked_widget)

        self.stacked_widget.insertWidget(self.__class__.GENERAL_DATA, self.table)
        self.stacked_widget.insertWidget(self.__class__.ITEM_DETAILS, self.item_type_screen)
        self.stacked_widget.insertWidget(self.__class__.SEARCH, self.search_screen)

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
    
    def display_popular_genres(self):
        self.display_general_data(self.sql.get_popular_genres())

    def display_most_loaned_items(self):
        self.display_general_data(self.sql.get_most_loaned_items())

    def display_least_loaned_items(self):
        self.display_general_data(self.sql.get_least_loaned_items())
    
    def display_most_held_items(self):
        self.display_general_data(self.sql.get_most_held_items())

    def display_least_held_items(self):
        self.display_general_data(self.sql.get_least_held_items())
        
    def display_items_at_location(self):
        self.display_search()
        self.search_screen.set_on_search(lambda id: self.search_screen.table.display(self.sql.get_items_from_location(str(id))))

    def display_item_type(self, id):
        self.item_type_screen.display_item(self.sql.get_item_type_info(str(id)))
        self.stacked_widget.setCurrentIndex(self.__class__.ITEM_DETAILS)

    def display_item_loan_history(self):
        self.display_search()
        self.search_screen.set_on_search(lambda id: self.search_screen.table.display(self.sql.get_item_loan_history(str(id))))

    def display_item_hold_history(self):
        self.display_search()
        self.search_screen.set_on_search(lambda id: self.search_screen.table.display(self.sql.get_item_hold_history(str(id))))

    def display_user_loan_history(self):
        self.display_search()
        self.search_screen.set_on_search(lambda id: self.search_screen.table.display(self.sql.get_user_loan_history(str(id))))

    def display_user_hold_history(self):
        self.display_search()
        self.search_screen.set_on_search(lambda id: self.search_screen.table.display(self.sql.get_user_hold_history(str(id))))


    def display_user_holds(self):
        self.display_search()
        self.search_screen.set_on_search(lambda id: self.search_screen.table.display(self.sql.get_user_holds(id)))

    def display_general_data(self, sql_result : SQLResult|None = None):
        if sql_result is not None:
            self.table.display(sql_result)
        else:
            self.table.clear()
        self.stacked_widget.setCurrentIndex(self.__class__.GENERAL_DATA)
    
    def display_search(self):
        self.search_screen.clear()
        self.stacked_widget.setCurrentIndex(self.__class__.SEARCH)

        # Close the sql connection when the window is closed
    def closeEvent(self, event):
        print("Closing...")
        self.sql.close()
        event.accept()
