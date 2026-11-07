from PyQt6.QtWidgets import QHBoxLayout, QLayout, QPushButton, QWidget

class Menu(QWidget):
    def __init__(self):
        super().__init__()

        layout : QLayout = QHBoxLayout()

        self.setLayout(layout)

    def add_button(self, button_text, button_action):
        button = QPushButton(button_text)
        button.clicked.connect(button_action)
        self.layout().addWidget(button)
