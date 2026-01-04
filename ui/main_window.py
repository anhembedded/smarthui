from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel
from ui.dashboard_tab import DashboardTab
from ui.hui_list_tab import HuiListTab
from ui.reports_tab import ReportsTab
from storage import get_initial_data, save_data
from app.services.members_service import MembersService
from app.ui.views.members_view import MembersView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartHui - Quản Lý Hụi 4.0")
        self.resize(1200, 800)
        
        self.data = get_initial_data()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self.header = QLabel("SmartHui")
        self.header.setProperty("heading", True)
        self.layout.addWidget(self.header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.dashboard_tab = DashboardTab(self.data)
        self.hui_list_tab = HuiListTab(self.data, self.save_state)
        
        self.members_service = MembersService(self.data.members, self.data.groups, self.data.transactions)
        self.members_tab = MembersView(self.members_service, self.save_state)
        
        self.reports_tab = ReportsTab(self.data)
        
        self.tabs.addTab(self.dashboard_tab, "Tổng Quan")
        self.tabs.addTab(self.hui_list_tab, "Quản Lý Dây Hụi")
        self.tabs.addTab(self.members_tab, "Thành Viên")
        self.tabs.addTab(self.reports_tab, "Báo Cáo & AIAT")
        
    def save_state(self):
        save_data(self.data)
        self.refresh_ui()

    def refresh_ui(self):
        # Notify tabs to refresh if needed
        self.dashboard_tab.refresh()
        self.hui_list_tab.refresh()
        self.members_tab.refresh()
        self.reports_tab.refresh()
