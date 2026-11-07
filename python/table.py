from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

class Table(QWidget):
    def __init__(self):
        super().__init__()

        self.data_widget = QWidget()
        self.data_widget.setLayout(QGridLayout())

        self.scroll_area : QScrollArea = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.data_widget)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.scroll_area)

    def clear(self):
        for i in reversed(range(self.data_widget.layout().count())):
            self.data_widget.layout().itemAt(i).widget().deleteLater()

    def display(self, header_row, content):
        self.clear()

        for i in range(len(header_row)):
            label : QLabel = QLabel(str(header_row[i]))
            label.setMaximumHeight(16)
            self.data_widget.layout().addWidget(label, 0, i)

        
        for row in range(len(content)):
            for i in range(len(content[row])):
                label : QLabel = QLabel(str(content[row][i]))
                label.setMaximumHeight(16)
                self.data_widget.layout().addWidget(label, row + 1, i)
        
        self.scroll_area.verticalScrollBar().setValue(0)
        

