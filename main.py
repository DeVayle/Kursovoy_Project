import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget
from authorization import AuthForm
from game_catalogue import GameCatalogForm
from plan_catalogue import SubscriptionCatalogForm
from admin_panel import AdminPanelForm
from db_manager import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное окно")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.auth_form = AuthForm(self)
        self.game_catalog_form = GameCatalogForm(self)
        self.subscription_catalog_form = SubscriptionCatalogForm(self)
        self.admin_panel_form = AdminPanelForm(self)

        self.stacked_widget.addWidget(self.auth_form)
        self.stacked_widget.addWidget(self.game_catalog_form)
        self.stacked_widget.addWidget(self.subscription_catalog_form)
        self.stacked_widget.addWidget(self.admin_panel_form)

        self.stacked_widget.setCurrentWidget(self.auth_form)

    def show_auth_form(self):
        self.stacked_widget.setCurrentWidget(self.auth_form)

    def show_game_catalog_form(self):
        self.stacked_widget.setCurrentWidget(self.game_catalog_form)

    def show_subscription_catalog_form(self):
        self.stacked_widget.setCurrentWidget(self.subscription_catalog_form)

    def show_admin_panel_form(self):
        self.stacked_widget.setCurrentWidget(self.admin_panel_form)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Подтверждение выхода', 'Вы уверены, что хотите выйти?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())