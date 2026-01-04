from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QColor, QPalette

def APPLY_STYLES(app: QApplication):
    app.setStyle("Fusion")
    
    # --- MODERN PALETTE (Tailwind-ish) ---
    # Emerald 600: #059669
    # Emerald 500: #10B981
    # Slate 50: #F8FAFC
    # Slate 100: #F1F5F9
    # Slate 200: #E2E8F0
    # Slate 700: #334155
    # Slate 800: #1E293B
    # Red 500: #EF4444
    
    # --- QPALETTE CONFIG FOR FUSION ---
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#334155"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F1F5F9"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#334155"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#334155"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#334155"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#EF4444"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#10B981"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#10B981"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)
    
    # --- FONTS ---
    # Use Segoe UI on Windows for that native clean look, fallback to Sans
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    
    # --- GLOBAL STYLESHEET ---
    app.setStyleSheet("""
        /* Main Window & Containers */
        QMainWindow {
            background-color: #F8FAFC;
        }
        QWidget {
            color: #334155;
            outline: none;
        }

        /* TABS (Modern Pill Style or Clean Tabs) */
        QTabWidget::pane {
            border: 1px solid #E2E8F0;
            background: #FFFFFF;
            border-radius: 8px;
            margin-top: 10px;
        }
        
        QTabWidget::tab-bar {
            alignment: left;
        }
        
        QTabBar::tab {
            background: transparent;
            color: #64748B;
            padding: 8px 20px;
            margin-right: 8px;
            font-weight: 600;
            border-bottom: 3px solid transparent;
        }
        
        QTabBar::tab:selected {
            color: #059669; /* Emerald 600 */
            border-bottom: 3px solid #059669;
        }
        
        QTabBar::tab:hover {
            color: #10B981;
            background-color: #F1F5F9;
            border-radius: 4px;
        }

        /* BUTTONS */
        QPushButton {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 8px 16px;
            border-radius: 6px;
            color: #475569;
            font-weight: 600;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #F8FAFC;
            border-color: #CBD5E1;
            color: #1E293B;
        }
        QPushButton:pressed {
            background-color: #F1F5F9;
        }
        
        /* Primary Button */
        QPushButton[primary="true"] {
            background-color: #10B981; /* Emerald 500 */
            color: #FFFFFF;
            border: 1px solid #059669;
        }
        QPushButton[primary="true"]:hover {
            background-color: #059669; /* Emerald 600 */
        }
        QPushButton[primary="true"]:pressed {
            background-color: #047857;
        }

        /* Danger Button */
        QPushButton[danger="true"] {
            background-color: #EF4444;
            color: white;
            border: 1px solid #DC2626;
        }
        QPushButton[danger="true"]:hover {
            background-color: #DC2626;
        }

        /* INPUTS */
        QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
            padding: 8px;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            background: #FFFFFF;
            color: #334155;
            selection-background-color: #10B981;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 1px solid #10B981;
            background-color: #FFFFFF;
        }
        QLineEdit:read-only {
            background-color: #F8FAFC;
            color: #64748B;
        }

        /* TABLES */
        QTableWidget {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            gridline-color: #F1F5F9;
            selection-background-color: #ECFDF5; /* Emerald 50 */
            selection-color: #064E3B; /* Emerald 900 */
        }
        QHeaderView::section {
            background-color: #F8FAFC;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #E2E8F0;
            font-weight: bold;
            color: #475569;
            font-size: 13px;
        }
        QTableWidget::item {
            padding: 5px;
            border-bottom: 1px solid #F1F5F9;
        }

        /* SCROLL BARS */
        QScrollBar:vertical {
            border: none;
            background: #F1F5F9;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #CBD5E1;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94A3B8;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        /* DIALOGS */
        QDialog {
            background-color: #FFFFFF;
        }
        
        /* CARD (Custom Property) */
        QLabel[cardTitle="true"] {
            font-size: 14px;
            font-weight: 600;
            color: #64748B;
        }
        QLabel[cardValue="true"] {
            font-size: 28px;
            font-weight: bold;
            color: #1E293B;
        }
        
        /* HEADINGS */
        QLabel[heading="true"] {
            font-size: 24px;
            font-weight: 800;
            color: #1E293B;
            margin-bottom: 10px;
        }
        QLabel[subheading="true"] {
            font-size: 16px;
            font-weight: 600;
            color: #475569;
        }
        
        /* SPLITTER */
        QSplitter::handle {
            background: #E2E8F0;
        }
    """)
