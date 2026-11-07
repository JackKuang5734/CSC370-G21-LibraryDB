from email import header
import sys
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QScrollArea, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton
from view import MainView
from table import Table
from sql_executor import SQLExecutor
from model import Model

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    model = Model()
    widget = MainView(model)
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())