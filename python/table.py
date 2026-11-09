from ctypes import alignment
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from sql_executor import SQLResult

class ClickableLabel(QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()


class Table(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(QVBoxLayout())
        
        self.grid : QGridLayout = QGridLayout()
        self.data_widget = QWidget()
        self.data_widget.setLayout(self.grid)

        self.scroll_area : QScrollArea = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.data_widget)
        
        self.layout().addWidget(self.scroll_area)
        self.layout().addStretch()

    def clear(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().deleteLater()

    def display(self, sql_result : SQLResult):
        self.clear()

        for i in range(len(sql_result.header)):
            label = QLabel(str(sql_result.header[i]))
            label.setMaximumHeight(16)
            self.grid.addWidget(label, 0, i)
        
        for col in range(len(sql_result.header)):
            link_function : function = None if len(sql_result.links) <= col else sql_result.links[col]
            for row in range(len(sql_result.rows)):
                label = ClickableLabel(str(sql_result.rows[row][col]))
                label.setMaximumHeight(16)
                if link_function is not None and sql_result.id_rows[row][col] is not None:
                    label.clicked.connect(lambda checked=False, func=link_function, val=sql_result.id_rows[row][col]: func(val))
                    label.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                self.grid.addWidget(label, row + 1, col)

        # self.setMaximumHeight((16 + 2 * self.grid.verticalSpacing()) * (len(sql_result.rows) + 1))


    # def display(self, header, rows):
    #     self.clear()

    #     for i in range(len(header)):
    #         label : QLabel = QLabel(str(header[i]))
    #         label.setMaximumHeight(16)
    #         self.data_widget.layout().addWidget(label, 0, i)

        
    #     for row in range(len(rows)):
    #         for i in range(len(rows[row])):
    #             label : QLabel = QLabel(str(rows[row][i]))
    #             label.setMaximumHeight(16)
    #             self.data_widget.layout().addWidget(label, row + 1, i)
        
    #     self.scroll_area.verticalScrollBar().setValue(0)
        
    
