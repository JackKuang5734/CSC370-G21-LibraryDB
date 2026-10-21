import sys
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QScrollArea, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton
from table import Table
from sql_executor import SQLExecutor

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.sql = SQLExecutor()
        self.table = Table()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.table)

        user_button = QPushButton("User")
        user_button.clicked.connect(self.display_users)
        hold_button = QPushButton("Hold")
        hold_button.clicked.connect(self.display_holds)
        loan_button = QPushButton("Loan")
        loan_button.clicked.connect(self.display_loans)
        itemtype_button = QPushButton("ItemType")
        itemtype_button.clicked.connect(self.display_item_types)
        item_button = QPushButton("Items")
        item_button.clicked.connect(self.display_items)
        location_button = QPushButton("Location")
        location_button.clicked.connect(self.display_locations)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(user_button)
        self.button_layout.addWidget(hold_button)
        self.button_layout.addWidget(loan_button)
        self.button_layout.addWidget(itemtype_button)
        self.button_layout.addWidget(item_button)
        self.button_layout.addWidget(location_button)

        self.layout : QVBoxLayout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

    def display_users(self):
        rows = self.sql.select("user_name, user_email, user_status", "user")
        self.table.display(("user_name", "user_email", "user_status"), rows)

    def display_holds(self):
        rows = self.sql.select("item_type_id, user_id, location_id, hold_created_date, hold_expiry_date, queue_number, hold_status", "hold")
        self.table.display(("item_type_id", "user_id", "location_id", "hold_created_date", "hold_expiry_date", "queue_number", "hold_status"), rows)
    
    def display_loans(self):
        rows = self.sql.select("item_id, user_id, location_id, checkout_date, due_date, loan_status", "loan")
        self.table.display(("item_id", "user_id", "location_id", "checkout_date", "due_date", "loan_status"), rows)

    def display_item_types(self):
        rows = self.sql.select("item_title, item_author, item_release_date, item_type", "itemtype")
        self.table.display(("item_title", "item_author", "item_release_date", "item_type"), rows)

    def display_items(self):
        rows = self.sql.query(
            """
SELECT it.item_title, l.location_name, i.item_status
FROM Item i
JOIN ItemType it
ON i.item_type_Id = it.item_type_id
JOIN Location l
ON i.location_id = l.location_id"""
        )
        self.table.display(("Item Title", "Location", "Status"), rows)

        pass

    def display_locations(self):
        rows = self.sql.select("location_name", "location")
        self.table.display(("location_name",), rows)

    def clicked(self):
        rows = self.sql.select("genre_id, genre_name", "genre")
        self.table.display(("genre_id", "genre_name"), rows)

    # Close the sql connection when the window is closed
    def closeEvent(self, event):
        print("Closing...")
        self.sql.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())