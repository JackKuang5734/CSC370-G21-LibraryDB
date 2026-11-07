


from cProfile import label
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from data_objects import ItemType


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
Genres: {item_type.genres}
""")