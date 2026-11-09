from email import header
import sys
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QScrollArea, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton
from view import MainView
from table import Table
from sql_executor import SQLExecutor

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    sql = SQLExecutor()
    widget = MainView(sql)
    widget.resize(800, 600)
    widget.show()
    
    sys.exit(app.exec())