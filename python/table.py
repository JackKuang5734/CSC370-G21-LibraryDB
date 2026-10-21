from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame


class Table(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout : QGridLayout = QGridLayout()

        self.setLayout(self.layout)

    def clear(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()

    def display(self, header_row, content):
        self.clear()

        for i in range(len(header_row)):            
            self.layout.addWidget(QLabel(str(header_row[i])), 0, i)

        for row in range(len(content)):
            for i in range(len(content[row])):
                self.layout.addWidget(QLabel(str(content[row][i])), row + 1, i)
        