from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from data_models import AppState
import qtawesome as qta

class StatCard(QFrame):
    def __init__(self, title, value, icon_name, color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {color};
            }}
        """)
        
        # Add slight shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Icon & Header row
        header_layout = QGridLayout()
        
        # Icon
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(24, 24))
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        
        # Title
        lbl_title = QLabel(title)
        lbl_title.setProperty("cardTitle", True)
        lbl_title.setStyleSheet("border: none; background: transparent;")
        
        layout.addWidget(icon_lbl)
        layout.addWidget(lbl_title)
        
        # Value
        lbl_value = QLabel(str(value))
        lbl_value.setProperty("cardValue", True)
        lbl_value.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(lbl_value)

class DashboardTab(QWidget):
    def __init__(self, data: AppState):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("Tổng Quan")
        title.setProperty("heading", True)
        subtitle = QLabel("Theo dõi tình hình hụi và dòng tiền")
        subtitle.setStyleSheet("color: #64748B; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.main_layout.addLayout(header_layout)
        
        # Grid for stats
        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        self.main_layout.addLayout(self.grid)
        
        self.render_stats()

    def render_stats(self):
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        total_members = len(self.data.members)
        active_groups = len([g for g in self.data.groups if g.status == 'Đang chạy'])
        total_groups = len(self.data.groups)
        
        # Calculate total flow
        total_in = sum(t.amount for t in self.data.transactions if t.type == 'CONTRIBUTE')
        total_out = sum((t.netAmount or t.amount) for t in self.data.transactions if t.type == 'COLLECT')
        
        # Add Cards with Icons
        self.grid.addWidget(StatCard("Tổng Thành Viên", str(total_members), "fa5s.users", "#3B82F6"), 0, 0)
        self.grid.addWidget(StatCard("Dây Hụi Đang Chạy", f"{active_groups}/{total_groups}", "fa5s.list-alt", "#10B981"), 0, 1)
        self.grid.addWidget(StatCard("Tổng Tiền Đã Đóng", f"{total_in:,.0f} đ", "fa5s.arrow-down", "#EF4444"), 1, 0)
        self.grid.addWidget(StatCard("Tổng Tiền Đã Hốt", f"{total_out:,.0f} đ", "fa5s.arrow-up", "#F59E0B"), 1, 1)

    def refresh(self):
        self.render_stats()
