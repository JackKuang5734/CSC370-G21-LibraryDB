from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QWidget


class Table(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(QGridLayout())

    def clear(self):
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().deleteLater()

    def display(self, header_row, content):
        self.clear()

        for i in range(len(header_row)):
            label : QLabel = QLabel(str(header_row[i]))
            label.setMaximumHeight(16)
            self.layout().addWidget(label, 0, i)

        
        for row in range(len(content)):
            for i in range(len(content[row])):
                label : QLabel = QLabel(str(content[row][i]))
                label.setMaximumHeight(16)
                self.layout().addWidget(label, row + 1, i)

