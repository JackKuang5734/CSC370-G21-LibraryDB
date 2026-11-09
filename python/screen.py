from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from data_objects import ItemType
from table import Table


class ItemInfomationScreen(QWidget):

    def __init__(self, main_view):
        super().__init__()
        
        self.main_view = main_view

        self.setLayout(QVBoxLayout())

        self.label = QLabel()
        self.layout().addWidget(self.label)


    def display_item(self, item_type : ItemType):
        self.label.setText(f"""{item_type.title}
By: {item_type.author}
Published by: {item_type.publisher}
Date: {item_type.release_date}
Type: {item_type.type}
Genres: {", ".join(item_type.genres)}
""")
        



class SearchScreen(QWidget):

    def __init__(self, main_view):
        super().__init__()

        self.main_view = main_view

        self.setLayout(QVBoxLayout())

        self.search_bar = QWidget()
        self.search_bar.setLayout(QHBoxLayout())
        
        self.search_text = QLineEdit()
        self.search_text.setMaximumHeight(16)
        self.search_text.returnPressed.connect(self.search)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search)
        self.search_button.setMaximumHeight(32)

        self.search_bar.layout().addWidget(self.search_text)
        self.search_bar.layout().addWidget(self.search_button)

        self.layout().addWidget(self.search_bar)
        
        self.table = Table()

        self.layout().addWidget(self.table)

    def set_on_search(self, search_function):
        self.search_function = search_function

    def search(self):
        self.search_function(self.search_text.text())
    
    def clear(self):
        self.search_function = None
        self.search_text.setText("")
        self.table.clear()