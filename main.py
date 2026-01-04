import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import APPLY_STYLES

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SmartHui - Quản Lý Hụi 4.0")
    
    # Apply global styles
    APPLY_STYLES(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
