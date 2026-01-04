from abc import ABC, abstractmethod
import sys
from PySide6.QtWidgets import QApplication

class AbstractUI(ABC):
    @abstractmethod
    def run(self):
        pass

class AbstractUIFactory(ABC):
    @abstractmethod
    def create_ui(self) -> AbstractUI:
        pass

# --- QtWidgets Implementation ---

class QtWidgetsUI(AbstractUI):
    def run(self):
        from ui.main_window import MainWindow
        from ui.styles import APPLY_STYLES

        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("SmartHui - Quản Lý Hụi 4.0")

        APPLY_STYLES(app)

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

class QtWidgetsFactory(AbstractUIFactory):
    def create_ui(self) -> AbstractUI:
        return QtWidgetsUI()

# --- QML Implementation ---

class QmlUI(AbstractUI):
    def run(self):
        from qml_ui.qml_runner import run_qml_ui
        run_qml_ui()

class QMLFactory(AbstractUIFactory):
    def create_ui(self) -> AbstractUI:
        return QmlUI()
