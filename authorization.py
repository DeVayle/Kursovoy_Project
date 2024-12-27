from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFrame)
from PyQt5.QtCore import Qt

class AuthForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Авторизация')
        self.setMinimumSize(300, 150)

        # Создаем центральный фрейм
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setLineWidth(1)
        self.frame.setFixedSize(400, 200)  # Фиксированный размер фрейма

        # Элементы формы
        self.label = QLabel('Авторизация')
        self.login_label = QLabel('Логин:')
        self.login_input = QLineEdit()
        self.password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.enter_button = QPushButton('Войти')

        # Размещение элементов внутри фрейма
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        frame_layout.addWidget(self.login_label)
        frame_layout.addWidget(self.login_input)
        frame_layout.addWidget(self.password_label)
        frame_layout.addWidget(self.password_input)
        frame_layout.addStretch(1)
        frame_layout.addWidget(self.enter_button)
        frame_layout.addStretch(1)
        self.frame.setLayout(frame_layout)

        # Размещение фрейма в главном окне
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.frame, alignment=Qt.AlignCenter)  # Центрируем фрейм
        self.setLayout(main_layout)

        self.enter_button.clicked.connect(self.check_credentials)

    def check_credentials(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if login == '' and password == '':
            self.main_window.show_game_catalog_form()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль!')